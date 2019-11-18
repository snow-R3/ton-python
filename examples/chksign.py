"""
https://test.ton.org/fiftbase.pdf#page=30&zoom=100,0,172
"""

from fift.fift import *


@script()
def main():
    pos_neg_cond = (cond('0<')
        .pos(String('negative').print())
        .neg(String('positive').print()))

    check_sign = word('check_sign', dupnz(), (cond()
        .pos(pos_neg_cond)
        .neg(String('zero').print())))

    check_sign(-17)
    check_sign(0)
    check_sign(3)


print(main())
