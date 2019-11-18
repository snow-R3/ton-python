from fift.fift import *


def test_create_empty_script():
    @script()
    def main():
        pass

    assert main() == ''


class TestStackManipulationWords:
    def test_dup(self):
        assert str(dup()) == 'dup'
        assert str(dup2()) == '2dup'
        assert str(dupnz()) == '?dup'

    def test_drop(self):
        assert str(drop()) == 'drop'
        assert str(drop2()) == '2drop'

    def test_swap(self):
        assert str(swap()) == 'swap'
        assert str(swap2()) == '2swap'

    def test_rot(self):
        assert str(rot()) == 'rot'
        assert str(nrot()) == '-rot'

    def test_over(self):
        assert str(over()) == 'over'

    def test_tuck(self):
        assert str(tuck()) == 'tuck'

    def test_nip(self):
        assert str(nip()) == 'nip'

    def test_pick(self):
        assert str(pick(0)) == '0 pick'

    def test_roll(self):
        assert str(roll(1)) == '1 roll'
        assert str(nroll(1)) == '1 -roll'

    def test_exch(self):
        assert str(exch(1)) == '1 exch'
        assert str(exch2(1, 3)) == '1 3 exch2'


class TestString:
    def test_create(self):
        assert str(string('abc')) == '"abc"'

    def test_print(self):
        assert str(string('abc').print()) == '."abc"'

    def test_cr(self):
        assert str(string('abc').print(cr=True)) == '."abc" cr'

    def test_concatenate(self):
        assert str(string('a', 'b', 'c', 1, 2)) == '"a" "b" $+ "c" $+ 1 (.) $+ 2 (.) $+'

    def test_multi_print(self):
        assert str(string('a', 'b', 'c', 1).print()) == '."a" ."b" ."c" 1 (.) type'

    def test_convert_number_to_str(self):
        assert str(string(1)) == '1 (.)'

    def test_usage(self):
        @script()
        def main():
            string('abc')
            string('a', 'b', 1)
            string('abc').print()
            string('abc').print(cr=True)

        assert main() == '"abc"\n' \
                         '"a" "b" $+ 1 (.) $+\n' \
                         '."abc"\n' \
                         '."abc" cr'


class TestInclude:
    def test_simple(self):
        assert str(include('Asm.fif')) == '"Asm.fif" include'

    def test_as_const(self):
        assert str(include('Asm.fif').const('asm')) == '"Asm.fif" include constant asm'


class TestConstants:
    def test_def_number(self):
        assert str(const('a', 1)) == '1 constant a'

    def test_def_number2(self):
        assert str(const('b', '2')) == '2 constant b'

    def test_def_string(self):
        assert str(const('c', string('abc'))) == '"abc" constant c'

    def test_def_dict(self):
        assert isinstance(const('d', {}), Dict)
        assert str(const('d', {})) == 'dictnew constant d'

    def test_add_to_dict(self):
        @script()
        def main():
            a = const('a', {})
            a.add(1, (4, 'u'), builder())
            a[2] = ((4, 'u'), builder())
            # generate an error if a key is duplicated
            a[2] = ((4, 'u'), builder(), 'Cannot be added')

        assert main() == 'dictnew constant a\n' \
                         '<b  b> <s 1 @\' a 4 udict! =: a\n' \
                         '<b  b> <s 2 @\' a 4 udict! =: a\n' \
                         '<b  b> <s 2 @\' a 4 udict!+ not abort"Cannot be added" =: a'

    def test_read(self):
        assert const('a', 1).read() == '@\' a'

    def test_read_predefined(self):
        assert str(const('$0')) == '@\' $0'

    def test_type(self):
        assert str(const('a', 1).type()) == '@\' a type'

    def test_usage(self):
        @script()
        def main():
            a = const('a', 1)
            b = const('b', 2)
            c = const('c', {})
            d = const('$0')

        assert main() == '1 constant a\n' \
                         '2 constant b\n' \
                         'dictnew constant c\n' \
                         '@\' $0'


class TestAssign:
    def test_simple(self):
        assert str(assign('a', 1)) == '1 =: a'

    def test_double(self):
        assert str(assign2('a', 1, 2)) == '1 2 2=: a'


class TestBlock:
    def test_empty_block(self):
        assert str(block()) == '{  }'


class TestWord:
    def test_empty_word(self):
        assert str(word('test')) == '{  } : test'

    def test_word_with_args(self):
        assert str(word('square', dup(), '*')) == '{ dup * } : square'

    def test_call_word(self):
        @script()
        def main():
            square = word('square', dup(), '*')
            square(2)

        assert main() == '{ dup * } : square\n' \
                         '2 square'

    def test_usage(self):
        @script()
        def main():
            square = word('square', dup(), '*')
            power5 = word('**5', square(square(dup())), '*')
            power5(3)

        assert main() == '{ dup * } : square\n' \
                         '{ dup square square * } : **5\n' \
                         '3 **5'


class TestBuilderPrimitive:
    def test_empty(self):
        assert str(builder()) == '<b  b>'

    def test_unsigned(self):
        assert str(builder().u(0, 32)) == '<b 0 32 u, b>'

    def test_signed(self):
        assert str(builder().i(2, 4)) == '<b 2 4 i, b>'

    def test_bytes(self):
        assert str(builder().b(swap())) == '<b swap B, b>'

    def test_bits(self):
        assert str(builder().s('b{1001}')) == '<b b{1001} s, b>'
        assert str(builder().s('x{4A}')) == '<b x{4A} s, b>'

    def test_ref(self):
        assert str(builder().r(swap())) == '<b swap ref, b>'

    def test_dict(self):
        assert str(builder().d()) == '<b null dict, b>'

    def test_inspect_empty(self):
        assert str(builder().inspect()) == '<b .s b>'

    def test_inspect_full(self):
        assert str(builder().u(3, 16).inspect()) == '<b 3 16 u, .s b>'

    def test_usage(self):
        @script()
        def main():
            d = const('d', {})
            builder().d(d)

        assert main() == 'dictnew constant d\n' \
                         '<b @\' d dict, b>'


class TestSlice:
    def test_create(self):
        assert str(slice()) == '<s '

    def test_u(self):
        assert str(slice().u(7)) == '<s 7 u@+'

    def test_s(self):
        assert str(slice().s(32)) == '<s 32 s@+'

    def test_b(self):
        assert str(slice().b(256)) == '<s 256 B@+'

    def test_r(self):
        assert str(slice().r()) == '<s ref@+'

    def test_d(self):
        assert str(slice().d()) == '<s dict@+'

    def test_multiple(self):
        assert str(slice().u(1).s(16).b(256).r().d()) == '<s 1 u@+ 16 s@+ 256 B@+ ref@+ dict@+'

    def test_silent(self):
        assert str(slice(silent=True).u(1).s(16)) == '<s 1 u@?+ 16 s@?+'

    def test_save_to_const(self):
        @script()
        def main():
            a = const('a', 'null')
            b = const('b', 'null')
            slice().u(7, s2c=a).s(32, s2c=b)

        assert main() == 'null constant a\n' \
                         'null constant b\n' \
                         '<s 7 u@+ =: a 32 s@+ =: b'


class TestFile:
    def test_read(self):
        assert str(file('test.bin').read()) == '"test.bin" file>B'

    def test_write(self):
        assert str(file('test.bin').write()) == '"test.bin" B>file'

    def test_filename_from_const(self):
        @script()
        def main():
            fn = const('fn', String('test.bin'))
            file(fn).read()

        assert main() == '"test.bin" constant fn\n' \
                         '@\' fn file>B'

    def test_read_file_and_save_to_const(self):
        @script()
        def main():
            data = file('test.bin').read()
            const('fd', data)

        assert main() == '"test.bin" file>B constant fd'

    def test_deserialize(self):
        @script()
        def main():
            file('test.bin').deserialize().u(7).s(2).b(256).r()

        assert main() == '"test.bin" file>B B>boc\n' \
                         '<s 7 u@+ 2 s@+ 256 B@+ ref@+'

    def test_deserialize_to_constants(self):
        @script()
        def main():
            c = const('c', 'null')
            d = const('d', 'null')
            (file('test.bin').deserialize()
                .u(7)
                .s(2)
                .b(256, s2c=c)
                .r(s2c=d))

        assert main() == 'null constant c\n' \
                         'null constant d\n' \
                         '"test.bin" file>B B>boc\n' \
                         '<s 7 u@+ 2 s@+ 256 B@+ =: c ref@+ =: d'


class TestIsDefined:
    def test_is_def(self):
        assert str(is_def('$1')) == 'def? $1'


class TestIf:
    def test_if(self):
        assert str(is_def('$1')) == 'def? $1'


class TestCond:
    def test_empty(self):
        assert str(cond()) == '{  } {  } cond'

    def test_simple(self):
        assert str(cond(
            1,
            (String('true').print(),),
            (String('false').print(),))) == '1 { ."true" } { ."false" } cond'

    def test_usage(self):
        @script()
        def main():
            check = word('?', (cond()
                .pos(String('true').print())
                .neg(String('false').print())))

            check(2, 3, '<')

        assert main() == '{ { ."true" } { ."false" } cond } : ?\n' \
                         '2 3 < ?'
