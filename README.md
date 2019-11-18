## Python to Fift language transformer [PROTOTYPE]

It's the prototype version and only has a little bit a part of Fift language 
possibility.

Fift language book [link](https://test.ton.org/fiftbase.pdf).

### Examples

Create an empty Fift script:
```python
from fift.fift import *

@script(out_filename='script.fif')
def main():
    # python code which will be transformed to Fift language
    pass

fift_code = main()
```
So, you can do something with the generated Fift code in `fift_code` variable or 
set an optional keyword argument `out_filename` and the code will be automatically
saved into the passed filename.

To run the code transformation you need to call a function `main` wrapped `@script` 
decorator. As a result you will get the generated Fift code.

#### Include another Fift script

```python
from fift.fift import *

@script()
def main():
    # will be transformed as `"Asm.fif" include`
    include('Asm.fif')
    include('TonUtil.fif')

main()
```

#### Work with strings

```python
from fift.fift import *

@script()
def main():
    # Transforms in: `"abc"`
    string('abc')
    # Concatenation of many string values. Transforms in: `"a" "b" $+ 1 (.) $+`
    string('a', 'b', 1)
    # Transforms in: `."abc"`
    string('abc').print()
    # Transforms in: `."abc" cr`
    string('abc').print(cr=True)
    
    # Convert a constant with number value to string value
    # Transforms in: `1 constant a`
    a = const('a', 1)
    # Transforms in: `@' a (.) =: a`
    assign(a, string(a))

main()
```

#### Create the new word and its usage

```python
from fift.fift import *

@script()
def main():
    # Transforms in: `{ dup * } : square`
    square = word('square', dup(), '*')
    # `2 square`
    square(2)
    # `{ dup square square * } : **5`
    power5 = word('**5', square(square(dup())), '*')
    power5(3)

main()
```

#### Create the different constants

```python
from fift.fift import *

@script()
def main():
    # create a constant with name `a` and value `1`
    a = const('a', 1)
    
    # will be transformed as `dictnew constant d`
    d = const('d', {})
    # if a constant created with `{}` value the result variable will have `Dict` interface
    # and you can add a new value to the created dict with using the next ways
    # where:
    #   1 : it's the key
    #   (4, 'u') : the key size and type (u - unsigned, i - signed)
    #   builder() : the value. Transformed as `<b  b>`. Also, you can pass another entity as value.
    d.add(1, (4, 'u'), builder())
    d[2] = ((4, 'u'), builder())
    
    # create the string constant
    const('c', String('abc'))

main()
```

#### Construct the builder

```python
from fift.fift import *

@script()
def main():
    # create an empty builder and will be transformed as `<b  b>`
    builder()
    # `<b 0 32 u, b>`
    builder().u(0, 32)
    # `<b 2 4 i, b>`
    builder().i(2, 4)
    # `<b swap B, b>`
    builder().b(swap())
    # `<b swap ref, b>`
    builder().r(swap())
    # `<b b{1001} s, b>`
    builder().s('b{1001}')
    # `<b 3 16 u, .s b>`
    builder().u(3, 16).inspect()
    # `<b 0 32 u, 2 4 i, b>`
    builder().u(0, 32).i(2, 4)

main()
```

#### Work with files (read, write and data deserialization)

```python
from fift.fift import *

@script()
def main():
    # read a file. Transforms in `"test.bin" file>B`
    file('test.bin').read()
    # write to file. Transforms in `"test.bin" B>file`
    file('test.bin').write()
    # deserialize data from a file
    # transforms in `"test.bin" file>B B>boc <s 7 u@+ 2 s@+ 256 B@+ ref@+`
    file('test.bin').deserialize().u(7).s(2).b(256).r()

    # deserialize data and safe something to constants
    # transforms in:
    #   null constant a
    #   null constant b
    #   "test.bin" file>B B>boc <s 7 u@+ 2 s@+ 256 B@+ =: c ref@+ =: d
    a = const('a', 'null')
    b = const('b', 'null')
    (file('test.bin').deserialize()
        .u(7)
        .s(2)
        .b(256, const=a)
        .r(const=b))

main()
```

#### Create a block

```python
from fift.fift import *

@script()
def main():
    # Transforms in: `{  }`
    block()

main()
```

*** Also to understand how it works you can look at the python tests.