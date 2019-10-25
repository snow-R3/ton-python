import inspect
import typing as t


__SCRIPTS__ = {}


class String:
    def __init__(self, *args):
        self._args = args

    def __str__(self):
        return '"%s"' % self._args[0]


def seq(*args, separator=' '):
    return separator.join(
        isinstance(a, dict) and 'dictnew' or str(a) for a in args if a is not None
    )


class Interface:
    def __init__(self, *args):
        self._lines = None
        self._args = args

    def set_lines(self, lines):
        self._lines = lines


def method(max_level=1):
    def wrap(f):
        def wrap2(*args, **kwargs):
            outer_frames = inspect.getouterframes(inspect.currentframe())
            frame_index = 1
            while True:
                script_conf = __SCRIPTS__.get(outer_frames[frame_index].function)
                if script_conf is not None:
                    break
    
                frame_index += 1
                if max_level is not None and frame_index > max_level:
                    break
    
            res = f(*args, **kwargs)

            if script_conf is not None:
                if isinstance(res, Interface):
                    res.set_lines(script_conf['_lines'])

                # remove previous code line if there is not Constant/Define
                if any(
                    isinstance(arg, Interface)
                    and not isinstance(arg, Const)
                    for arg in args
                ):
                    script_conf['_lines'].pop()

                script_conf['_lines'].append(res)
    
            return res
        return wrap2
    return wrap


@method()
def swap():
    class Swap(Interface):
        def __str__(self):
            return 'swap'

    return Swap()


@method()
def dup():
    class Dup(Interface):
        def __str__(self):
            return 'dup'

    return Dup()


@method()
def drop():
    class Drop(Interface):
        def __str__(self):
            return 'drop'

    return Drop()


@method()
def rot():
    class Rot(Interface):
        def __str__(self):
            return 'rot'

    return Rot()


@method()
def dump():
    class Dump(Interface):
        def __str__(self):
            return '.s'

    return Dump()


@method()
def is_defined(exp):
    class IsDefined(Interface):
        def __str__(self):
            return 'def? %s {} {}' % (exp,)

    return IsDefined()


@method()
def builder():
    class Builder(Interface):
        def __init__(self):
            super(Builder, self).__init__()
            self._inspect = False
            self._args = []

        def __str__(self):
            r = seq(*(
                isinstance(a, tuple) and seq(*a)
                or isinstance(a, Dict) and '%s dict' % a.read()
                for a in self._args

            ), separator=', ')

            return '<b %s%s b>' % (
                r and r + ',' or '',
                self._inspect and (r and ' ' or '') + '.s' or '')

        def inspect(self):
            self._inspect = True
            return self

        def u(self, val, size):
            self._args.append((val, size, 'u'))
            return self

        def i(self, val, size):
            self._args.append((val, size, 'i'))
            return self

        def b(self, val):
            self._args.append((val, 'B'))
            return self

        def s(self, val):
            self._args.append((val, 's'))
            return self

        def ref(self, val):
            self._args.append((val, 'ref'))
            return self

    return Builder()


@method()
def slice(*args, before_args=None):
    class Slice(Interface):
        def __init__(self, *args):
            super(Slice, self).__init__(*args)
            self._unpack_args = []

        def __str__(self):
            return '%s<s %s%s' % (
                before_args and seq(*before_args) + ' ' or '',
                seq(*self._args),
                (self._args and self._unpack_args and ' ' or '') + seq(*(seq(*ua) for ua in self._unpack_args)))

        def u(self, size, const=None):
            if const is None:
                v = (size, 'u@+')
            else:
                v = (assign(const, size, 'u@+'),)

            self._unpack_args.append(v)
            return self

        def s(self, size, const=None):
            if const is None:
                v = (size, 's@+')
            else:
                v = (assign(const, size, 's@+'),)

            self._unpack_args.append(v)
            return self

        def b(self, size, const=None):
            if const is None:
                v = (size, 'B@+')
            else:
                v = (assign(const, size, 'B@+'),)

            self._unpack_args.append(v)
            return self

        def ref(self, const=None):
            if const is None:
                v = ('ref@+',)
            else:
                v = (assign(const, 'ref@+'),)

            self._unpack_args.append(v)
            return self

    return Slice(*args)


@method()
def abort(text):
    return 'abort%s' % String(text)


class Const(Interface):
    def __init__(self, name, *args):
        super(Const, self).__init__(*args)

        self._name = name

    def get_name(self):
        return self._name

    name = property(get_name)

    def read(self):
        return '@\' %s' % self._name

    def __str__(self):
        return '%s constant %s' % (seq(*self._args), self._name,)

    def __add__(self, other):
        self._lines.append(seq(self.read(), other.read(), '+'))
        # return other


class Dict(Interface):
    size_map = {
        'i': 'idict!',
        'u': 'udict!',
    }

    def add(self, key, size: t.Tuple[int, str], val, exc: t.Union[bool, str] = False):
        """
        Examples:
            a.add(1, (4, 'u'), 2)
            a.add(2, (8, 'u'), 3, 'The new value cannot be added')
            a[2] = ((16, 'i'), 5, 'The new value cannot be added')
        """
        if isinstance(val, Interface):
            self._lines.pop()

        self._lines.append(assign(
            self._name,
            val, slice(key), self.read(), size[0],
            self.size_map[size[1]] + (exc and '+' or ''),
            exc and seq('not', abort(exc)) or None))

    def __setitem__(self, key, value):
        self.add(key, value[0], value[1], value[2] if len(value) > 2 else False)


@method(max_level=None)
def const(name, *args):
    is_dict = any(isinstance(a, dict) for a in args)

    cls = is_dict and type('Interface', (Dict, Const), {}) or Const
    return cls(name, *args)


class Assign(Interface):
    def __init__(self, name, *args):
        self._name = name

        super(Assign, self).__init__(*args)

    def __str__(self):
        return '%s =: %s' % (seq(*self._args), isinstance(self._name, Const) and self._name.name or self._name)


@method()
def assign(name, *args):
    return Assign(name, *args)


@method()
def include(name):
    class Include(Interface):
        def __str__(self):
            return '%s include' % String(name)

        def const(self, name):
            return const(name, self)

    return Include()


@method()
def file(name):
    class File(Interface):
        def __init__(self, *args):
            super(File, self).__init__(*args)
            self._deserialize = None

        def __str__(self):
            return str(self._deserialize)

        def read(self):
            return '%s file>B' % String(name)

        def write(self):
            return '%s B>file' % String(name)

        def deserialize(self, builder=None):
            self._deserialize = slice(before_args=('%s B>boc' % self.read(),))
            return self._deserialize

    return File()


@method()
def times(number, *args):
    class Times(Interface):
        def __init__(self, *args):
            super(Times, self).__init__(*args)
            self._before_args = None

        def __str__(self):
            return '%s{ %s } %s times' % (
                self._before_args and seq(*(
                    isinstance(a, Const) and a.read() or a
                    for a in self._before_args)) + ' ' or '',
                seq(*(
                    isinstance(a, Const) and a.name or a
                    for a in args)),
                number)

        def before(self, *args):
            self._before_args = args
            return self

    return Times()


def script(out_filename=None):
    def w(f):
        lines = []
        __SCRIPTS__[f.__name__] = {
            '_lines': lines
        }

        def w2(*args, **kwargs):
            f(*args, **kwargs)

            fift_code = '\n'.join(str(l) for l in lines)
            if out_filename is not None:
                with open(out_filename, 'w+') as of:
                    of.write(fift_code)

            return fift_code
        return w2
    return w
