## Python to Fift language transformer [PROTOTYPE]

It's the prototype version and only has a little bit a part of Fift language 
possibility.

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
decorator. As the result you will get the Fift code.

#### Include another Fift script

```python
from fift.fift import *

@script()
def main():
    # will be transformed as `"Asm.fif" include`
    include('Asm.fif')
    include('TonUtil.fif')
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
    c = const('c', String('abc'))
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
    builder().ref(swap())
    # `<b b{1001} s, b>`
    builder().s('b{1001}')
    # `<b 3 16 u, .s b>`
    builder().u(3, 16).inspect()
    # `<b 0 32 u, 2 4 i, b>`
    builder().u(0, 32).i(2, 4)
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
    file('test.bin').deserialize().u(7).s(2).b(256).ref()

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
        .ref(const=b))
```

#### Simple loops

```python
from fift.fift import *

@script()
def main():
    # Simple loop. Transforms in `1 { 1+ } 1 times`
    times(3, '1+').before(1)
    # Reads a value from a constant and sum itself in each iteration of the loop 
    # writing a new value to the constant
    # Transforms in:
    #   1 constant a
    #   @' a { dup + =: a } 3 times
    a = const('a', 1)
    times(3, assign(a, dup(), '+')).before(a)
```

*** Also to understand how it works you can look at the python tests.