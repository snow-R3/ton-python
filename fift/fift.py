import typing as t


_METHOD_RESULTS = []


class Interface:
    def __init__(self, *args):
        self._args = args
        self.structure = []
        self.ref = False
        self._created = False

    def get_args(self):
        return self._args

    args = property(get_args)

    def add_to_code(self, code_lines, level):
        if not self.ref:
            code_lines.append(self)


def _root_methods():
    for mr in _METHOD_RESULTS:
        if not mr.ref:
            yield mr


def _as_ref(args, res=None):
    for a in args:
        if isinstance(a, Interface):
            a.ref = True
            if res is not None:
                res.structure.append(a)


def method():
    def wrap(f):
        def wrap2(*args, **kwargs):
            res = f(*args, **kwargs)
            _METHOD_RESULTS.append(res)

            _as_ref(args, res)
            return res
        return wrap2
    return wrap


SCRIPTS = {}


def script(out_filename=None):
    global _METHOD_RESULTS
    _METHOD_RESULTS = []

    code_lines = []

    def code_lines_iter():
        for l in code_lines:
            s = str(l)
            if s:
                yield s

    def _inner(m, level=1):
        m.add_to_code(code_lines, level)

        for s in m.structure:
            level += 1
            _inner(s, level)
            level -= 1

    def w(f):
        SCRIPTS[f.__name__] = []

        def w2(*args, **kwargs):
            f(*args, **kwargs)

            for rm in _root_methods():
                _inner(rm)

            fift_code = '\n'.join(code_lines_iter())
            if out_filename is not None:
                with open(out_filename, 'w+') as of:
                    of.write(fift_code)

            return fift_code
        return w2
    return w


def seq(*args, separator=' '):
    return separator.join(str(a) for a in args if a is not None)


class Dup(Interface):
    def __init__(self, double=False, non_zero=False):
        super(Dup, self).__init__()
        self._double = double
        self._non_zero = non_zero

    def __str__(self):
        return '%sdup' % (self._non_zero and '?' or (self._double and '2' or ''))


@method()
def dup():
    return Dup()


@method()
def dup2():
    return Dup(double=True)


@method()
def dupnz():
    return Dup(non_zero=True)


class Drop(Interface):
    def __init__(self, double=False):
        super(Drop, self).__init__()
        self._double = double

    def __str__(self):
        return '%sdrop' % (self._double and '2' or '')


@method()
def drop():
    return Drop()


@method()
def drop2():
    return Drop(double=True)


class Swap(Interface):
    def __init__(self, double=False):
        super(Swap, self).__init__()
        self._double = double

    def __str__(self):
        return '%sswap' % (self._double and '2' or '')


@method()
def swap():
    return Swap()


@method()
def swap2():
    return Swap(double=True)


class Rot(Interface):
    def __init__(self, neg=False):
        super(Rot, self).__init__()
        self._neg = neg

    def __str__(self):
        return '%srot' % (self._neg and '-' or '')


@method()
def rot():
    return Rot()


@method()
def nrot():
    return Rot(neg=True)


class Over(Interface):
    def __str__(self):
        return 'over'


@method()
def over():
    return Over()


class Tuck(Interface):
    def __str__(self):
        return 'tuck'


@method()
def tuck():
    return Tuck()


class Nip(Interface):
    def __str__(self):
        return 'nip'


@method()
def nip():
    return Nip()


class Pick(Interface):
    def __init__(self, n):
        super(Pick, self).__init__()
        self._n = n

    def __str__(self):
        return '%s pick' % self._n


@method()
def pick(n):
    """
    0 pick is equivalent to dup, and 1 pick to over
    """
    return Pick(n)


class Roll(Interface):
    def __init__(self, n, neg=False):
        super(Roll, self).__init__()
        self._n = n
        self._neg = neg

    def __str__(self):
        return '%s %sroll' % (self._n, self._neg and '-' or '')


@method()
def roll(n):
    """
    1 roll is equivalent to swap, and 2 roll to rot
    """
    return Roll(n)


@method()
def nroll(n):
    """
    1 -roll is equivalent to swap, and 2 -roll to -rot
    """
    return Roll(n, neg=True)


class Exch(Interface):
    def __init__(self, n, m=None):
        super(Exch, self).__init__()
        self._n = n
        self._m = m

    def __str__(self):
        if self._m is None:
            return '%s exch' % self._n
        else:
            return '%s %s exch2' % (self._n, self._m)


@method()
def exch(n):
    """
    1 exch is equivalent to swap, and 2 exch to swap rot
    """
    return Exch(n)


@method()
def exch2(n, m):
    """
    """
    return Exch(n, m)


class Dump(Interface):
    def __str__(self):
        return '.s'


@method()
def dump():
    return Dump()


class Halt(Interface):
    def __init__(self, code):
        super(Halt, self).__init__()
        self._code = code

    def __str__(self):
        return '%s halt' % self._code


@method()
def halt(code):
    return Halt(code)


class Abort(Interface):
    def __init__(self, text):
        super(Abort, self).__init__()
        self._text = text

    def __str__(self):
        return 'abort%s' % String(self._text)


@method()
def abort(text):
    return Abort(text)


class String(Interface):
    def __init__(self, *args):
        super(String, self).__init__(*args)
        self._print = False
        self._cr = False

    def _g(self):
        for i, arg in enumerate(self._args):
            if isinstance(arg, str):
                r = '%s"%s"' % (self._print and '.' or '', arg)

            elif isinstance(arg, Const):
                if arg.args:
                    r = arg.read() + (isinstance(arg.args[-1], (int,)) and ' (.)' or '')
                else:
                    r = str(arg.type())
            else:
                r = '%s (.)%s' % (arg, self._print and ' type' or '')

            if not self._print:
                r += (i > 0 and ' $+' or '')

            yield r

    def __str__(self):
        return seq(*self._g()) + (self._cr and ' cr' or '')

    def print(self, cr=False):
        self._print = True
        self._cr = cr
        return self


@method()
def string(*args):
    return String(*args)


class Const(Interface):
    def __init__(self, name, *args):
        super(Const, self).__init__(*args)

        self._defined = False
        self._name = name
        self._type = False

    def __str__(self):
        if self._type:
            return '%s type' % self.read()

        if self._args:
            return '%s constant %s' % (seq(*self._args), self._name,)
        else:
            return self.read()

    def add_to_code(self, code_lines, level):
        if not self.ref:
            code_lines.append(self)

        elif not self._args:
            return

        elif not self._defined:
            self._defined = True
            code_lines.insert(len(code_lines) - 1, self)

    def get_name(self):
        return self._name

    name = property(get_name)

    def read(self):
        return '@\' %s' % self._name

    def type(self):
        self._type = True
        return self


class AddToDict(Interface):
    size_map = {
        'i': 'idict!',
        'u': 'udict!',
    }

    def __init__(self, interface, key, size, val, exc):
        super(AddToDict, self).__init__()
        self._interface = interface
        self._key = key
        self._size = size
        self._val = val
        self._exc = exc

    def __str__(self):
        args = [
            self._val,
            '<s', self._key,
            self._interface.read(),
            self._size[0],
            self.size_map[self._size[1]] + (self._exc and '+' or ''),
        ]
        if self._exc:
            args += ['not', abort(self._exc)]

        return str(Assign(self._interface.name, *args))


@method()
def add_to_dict(interface, key, size, val, exc):
    return AddToDict(interface, key, size, val, exc)


class Dict(Const):
    def __str__(self):
        return 'dictnew constant %s' % self._name

    def __setitem__(self, key, value):
        self.add(key, value[0], value[1], value[2] if len(value) > 2 else False)

    def add(self, key, size: t.Tuple[int, str], val, exc: t.Union[bool, str] = False):
        """
        Examples:
            a.add(1, (4, 'u'), 2)
            a.add(2, (8, 'u'), 3, 'The new value cannot be added')
            a[2] = ((16, 'i'), 5, 'The new value cannot be added')
        """

        add_to_dict(self, key, size, val, exc)
        return self


@method()
def const(name, *args):
    is_dict = args and isinstance(args[-1], dict)
    cls = is_dict and Dict or Const
    return cls(name, *args)


class Include(Interface):
    def __init__(self, name, *args):
        super(Include, self).__init__(*args)

        self._name = name

    def __str__(self):
        return '%s include' % String(self._name)

    def const(self, name):
        return const(name, self)


@method()
def include(name):
    return Include(name)


class Assign(Interface):
    def __init__(self, name, *args, double=False):
        super(Assign, self).__init__(*args)

        self._name = name
        self._double = double

    def _resolve_name(self):
        return isinstance(self._name, Const) and self._name.name or self._name

    def __str__(self):
        return '%s %s=: %s' % (
            seq(*self._args),
            self._double and '2' or '',
            self._resolve_name())


@method()
def assign(name, *args):
    return Assign(name, *args)


@method()
def assign2(name, *args):
    return Assign(name, *args, double=True)


class Block(Interface):
    def __str__(self):
        return '{ %s }' % seq(*self._args)


@method()
def block(*args):
    return Block(*args)


class Word(Interface):
    def __init__(self, name, *args):
        super(Word, self).__init__(*args)
        self._name = name

    def __str__(self):
        return '{ %s } : %s' % (
            seq(*(
                isinstance(a, Word) and a.name
                or a
                for a in self._args
            )),
            self._name)

    def __call__(self, *args, **kwargs):
        @method()
        def inner(name, *_args):
            class _I(Interface):
                def __str__(self):
                    return seq(seq(*_args), name)

            return _I()

        return inner(self.name, *args)

    def get_name(self):
        return self._name

    name = property(get_name)


@method()
def word(name, *args):
    return Word(name, *args)


class Builder(Interface):
    def __init__(self):
        super(Builder, self).__init__()
        self._inspect = False
        self._args = []

    def __str__(self):
        r = seq(*(seq(*a) for a in self._args), separator=', ')

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

    def r(self, val):
        self._args.append((val, 'ref'))
        return self

    def d(self, val='null'):
        self._args.append((isinstance(val, Const) and val.read() or val, 'dict'))
        return self


@method()
def builder():
    return Builder()


class Slice(Interface):
    def __init__(self, *args, silent=False):
        super(Slice, self).__init__(*args)
        self._unpack_args = []
        self._silent = silent

    def __str__(self):
        return '<s %s%s' % (
            seq(*self._args),
            (self._args and self._unpack_args and ' ' or '') + seq(*(seq(*ua) for ua in self._unpack_args)))

    def _symbol(self, v):
        return '%s@%s+' % (v, self._silent and '?' or '')

    def u(self, size, s2c=None):
        if s2c is None:
            v = (size, self._symbol('u'))
        else:
            v = (Assign(s2c.name, size, self._symbol('u')),)

        self._unpack_args.append(v)
        return self

    def s(self, size, s2c=None):
        if s2c is None:
            v = (size, self._symbol('s'))
        else:
            v = (Assign(s2c.name, size, self._symbol('s')),)

        self._unpack_args.append(v)
        return self

    def b(self, size, s2c=None):
        if s2c is None:
            v = (size, self._symbol('B'))
        else:
            v = (Assign(s2c.name, size, self._symbol('B')),)

        self._unpack_args.append(v)
        return self

    def r(self, s2c=None):
        if s2c is None:
            v = (self._symbol('ref'),)
        else:
            v = (Assign(s2c.name, self._symbol('ref')),)

        self._unpack_args.append(v)
        return self

    def d(self, s2c=None):
        if s2c is None:
            v = (self._symbol('dict'),)
        else:
            v = (Assign(s2c.name, self._symbol('dict')),)

        self._unpack_args.append(v)
        return self


@method()
def slice(*args, silent=False):
    return Slice(*args, silent=silent)


class ReadFromFile(Interface):
    def __init__(self, name):
        super(ReadFromFile, self).__init__()
        self._name = name

    def __str__(self):
        return '%s file>B' % self._name


@method()
def read_from_file(name):
    return ReadFromFile(name)


class WriteToFile(Interface):
    def __init__(self, name):
        super(WriteToFile, self).__init__()
        self._name = name

    def __str__(self):
        return '%s B>file' % self._name


@method()
def write_to_file(name):
    return WriteToFile(name)


class Deserialize(Interface):
    def __str__(self):
        return '%s B>boc' % seq(*self._args)


@method()
def deserialize(*args):
    return Deserialize(*args)


class File(Interface):
    def __init__(self, name):
        super(File, self).__init__()
        self._name = name

    def __str__(self):
        return ''

    def _resolve_name(self):
        return isinstance(self._name, Const) and self._name.read() or String(self._name)

    def read(self):
        return read_from_file(self._resolve_name())

    def write(self):
        return write_to_file(self._resolve_name())

    def deserialize(self):
        deserialize(ReadFromFile(self._resolve_name()))
        return slice()


@method()
def file(name):
    return File(name)


class IsDef(Interface):
    def __init__(self, word_name):
        super(IsDef, self).__init__()
        self._word_name = word_name

    def __str__(self):
        return 'def? %s' % (self._word_name,)


@method()
def is_def(word_name):
    return IsDef(word_name)


class Cond(Interface):
    def __init__(self, v=None, pos_args=None, neg_args=None):
        super(Cond, self).__init__()
        self._v = v
        self._pos_args = pos_args
        self._neg_args = neg_args

    def __str__(self):
        return '%s{ %s } { %s } cond' % (
            self._v is not None and str(self._v) + ' ' or '',
            self._pos_args and seq(*self._pos_args) or '',
            self._neg_args and seq(*self._neg_args) or '')

    def pos(self, *args):
        _as_ref(args)
        self._pos_args = args
        return self

    def neg(self, *args):
        _as_ref(args)
        self._neg_args = args
        return self


@method()
def cond(v=None, pos_args=None, neg_args=None):
    return Cond(v=v, pos_args=pos_args, neg_args=neg_args)
