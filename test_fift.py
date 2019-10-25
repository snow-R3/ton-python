from unittest import mock
from fift.fift import *


def test_empty_script():
    @script()
    def main():
        pass

    assert main() == ''


def test_save_script_to_file():
    with mock.patch('fift.fift.open', mock.mock_open()) as fift_code_file:
        @script(out_filename='test.fif')
        def main():
            const('a', 1)

        main()

        fift_code_file.assert_called_with('test.fif', 'w+')
        fift_code_file().write.assert_called_once_with('1 constant a')


def test_string():
    assert str(String('abc')) == '"abc"'


class TestInclude:
    def test_simple(self):
        assert str(include('Asm.fif')) == '"Asm.fif" include'

    def test_as_const(self):
        assert str(include('Asm.fif').const('asm')) == '"Asm.fif" include constant asm'


class TestFile:
    def test_read(self):
        assert file('test.bin').read() == '"test.bin" file>B'

    def test_write(self):
        assert file('test.bin').write() == '"test.bin" B>file'

    def test_deserialize(self):
        assert str(
            file('test.bin').deserialize()
            .u(7).s(2).b(256).ref()
        ) == '"test.bin" file>B B>boc <s 7 u@+ 2 s@+ 256 B@+ ref@+'

    def test_deserialize_to_constants(self):
        @script()
        def main():
            c = const('c', 'null')
            d = const('d', 'null')
            (file('test.bin').deserialize()
                .u(7)
                .s(2)
                .b(256, const=c)
                .ref(const=d))

        assert main() == 'null constant c\n' \
                         'null constant d\n' \
                         '"test.bin" file>B B>boc <s 7 u@+ 2 s@+ 256 B@+ =: c ref@+ =: d'


class TestTimes:
    def test_simple(self):
        assert str(times(1, '1+').before(1)) == '1 { 1+ } 1 times'

    def test_inc_const(self):
        @script()
        def main():
            a = const('a', 1)
            times(3, assign(a, '1+')).before(a)

        assert main() == '1 constant a\n' \
                         '@\' a { 1+ =: a } 3 times'


class TestConstants:
    def test_def_number(self):
        assert str(const('a', 1)) == '1 constant a'

    def test_def_number2(self):
        assert str(const('b', '2')) == '2 constant b'

    def test_def_string(self):
        assert str(const('c', String('abc'))) == '"abc" constant c'

    def test_def_dict(self):
        assert str(const('d', {})) == 'dictnew constant d'

    def test_add_to_dict(self):
        @script()
        def main():
            d = const('d', {})
            d.add(1, (4, 'u'), builder())
            d[2] = ((4, 'u'), builder())

        assert main() == 'dictnew constant d\n' \
                         '<b  b> <s 1 @\' d 4 udict! =: d\n' \
                         '<b  b> <s 2 @\' d 4 udict! =: d'

    def test_add_to_dict_exc(self):
        @script()
        def main():
            d = const('d', {})
            d.add(1, (4, 'u'), builder(), 'The new value cannot be added')

        assert main() == 'dictnew constant d\n' \
                         '<b  b> <s 1 @\' d 4 udict!+ not abort"The new value cannot be added" =: d'

    def test_read(self):
        assert const('a', 1).read() == '@\' a'

    def test_cell_const(self):
        assert str(const('a', builder())) == '<b  b> constant a'


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
        assert str(builder().ref(swap())) == '<b swap ref, b>'

    def test_inspect_empty(self):
        assert str(builder().inspect()) == '<b .s b>'

    def test_inspect_full(self):
        assert str(builder().u(3, 16).inspect()) == '<b 3 16 u, .s b>'
