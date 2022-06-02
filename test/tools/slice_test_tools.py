# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: slice_test_tools.py
@time: 2022/06/01
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import math
import random
import typing

COMMON_SLICE_TEST_CASES = [
    # arr[:]
    (None, None, None),
    # arr[::x]
    (None, None, 1), (None, None, 2), (None, None, 3),
    # arr[::-x]
    (None, None, -1), (None, None, -2), (None, None, -3),
    # arr[x::]
    (0, None, None), (20, None, None), (1, None, None), (100, None, None), (101, None, None),
    # arr[-x::]
    (-20, None, None), (-1, None, None), (-100, None, None), (-101, None, None),
    # arr[:x:]
    (None, 0, None), (None, 20, None), (None, 1, None), (None, 100, None), (None, 101, None),
    # arr[:-x:]
    (None, -20, None), (None, -1, None), (None, -100, None), (None, -101, None),
    # arr[x:x:]
    (0, 20, None), (20, 50, None), (20, 100, None), (20, 101, None), (50, 50, None),
    (20, 0, None), (50, 20, None), (100, 20, None), (101, 20, None),
    # arr[-x:x:]
    (-20, 50, None), (-20, 100, None), (-20, 101, None), (-50, 50, None),
    (-20, 0, None), (-50, 20, None), (-100, 20, None), (-101, 20, None),
    # arr[x:-x:]
    (0, -20, None), (20, -50, None), (20, -100, None), (20, -101, None), (50, -50, None),
    (50, -20, None), (100, -20, None), (101, -20, None),
    # arr[-x:-x:]
    (-20, -50, None), (-20, -100, None), (-20, -101, None), (-50, -50, None),
    (-50, -20, None), (-100, -20, None), (-101, -20, None),
    # arr[x::x]
    (0, None, 1), (100, None, 1), (99, None, 1),
    (0, None, 2), (20, None, 2), (100, None, 2), (101, None, 2),
    (10, None, 5), (40, None, 10), (0, None, 100), (10, None, 1), (80, None, 15),
    (101, None, 9999),
    # arr[x::-x]
    (0, None, -1), (100, None, -1), (99, None, -1),
    (0, None, -2), (20, None, -2), (100, None, -2), (101, None, -2),
    (10, None, -5), (40, None, -10), (0, None, -100), (10, None, -1), (80, None, -15),
    (101, None, -9999),
    # arr[-x::x]
    (-100, None, 1), (-100, None, 1), (-99, None, 1),
    (-20, None, 2), (-100, None, 2), (-101, None, 2),
    (-10, None, 5), (-40, None, 10), (-10, None, 1), (-80, None, 15),
    (-101, None, 9999),
    # arr[-x::-x]
    (-100, None, -1), (-100, None, -1), (-99, None, -1),
    (-20, None, -2), (-100, None, -2), (-101, None, -2),
    (-10, None, -5), (-40, None, -10), (-10, None, -1), (-80, None, -15),
    (-101, None, -9999),
    # arr[:x:x]
    (None, 0, 1), (None, 100, 1), (None, 99, 1),
    (None, 0, 2), (None, 20, 2), (None, 100, 2), (None, 101, 2),
    (None, 10, 5), (None, 40, 10), (None, 0, 100), (None, 10, 1), (None, 80, 15),
    (None, 101, 9999),
    # arr[:x:-x]
    (None, 0, -1), (None, 100, -1), (None, 99, -1),
    (None, 0, -2), (None, 20, -2), (None, 100, -2), (None, 101, -2),
    (None, 10, -5), (None, 40, -10), (None, 0, -100), (None, 10, -1), (None, 80, -15),
    (None, 101, -9999),
    # arr[:-x:x]
    (None, -100, 1), (None, -100, 1), (None, -99, 1),
    (None, -20, 2), (None, -100, 2), (None, -101, 2),
    (None, -10, 5), (None, -40, 10), (None, -10, 1), (None, -80, 15),
    (None, -101, 9999),
    # arr[:-x:-x]
    (None, -100, -1), (None, -100, -1), (None, -99, -1),
    (None, -20, -2), (None, -100, -2), (None, -101, -2),
    (None, -10, -5), (None, -40, -10), (None, -10, -1), (None, -80, -15),
    (None, -101, -9999),
    # arr[x:x:x]
    (0, 20, 1), (0, 20, 2), (0, 20, 10), (0, 20, 20), (0, 20, 21),
    (20, 50, 1), (20, 50, 10), (20, 50, 100),
    (0, 100, 1), (0, 111, 2), (1, 1, 1), (99, 100, 1), (100, 100, 1), (100, 101, 1),
    (101, 101, 1), (10, 101, 10), (1, 101, 10), (11, 111, 11),

    (20, 0, 1), (20, 0, 2), (20, 0, 10), (20, 0, 20), (20, 0, 21),
    (50, 20, 1), (50, 20, 10), (50, 20, 100),
    (100, 0, 1), (111, 0, 2), (100, 99, 1), (101, 100, 1),
    (101, 10, 10), (101, 1, 10), (111, 11, 11),
    # arr[x:x:-x]
    (0, 20, -1), (0, 20, -2), (0, 20, -10), (0, 20, -20), (0, 20, -21),
    (20, 50, -1), (20, 50, -10), (20, 50, -100),
    (0, 100, -1), (0, 111, -2), (1, 1, -1), (99, 100, -1), (100, 100, -1), (100, 101, -1),
    (101, 101, -1), (10, 101, -10), (1, 101, -10), (11, 111, -11),

    (20, 0, -1), (20, 0, -2), (20, 0, -10), (20, 0, -20), (20, 0, -21),
    (50, 20, -1), (50, 20, -10), (50, 20, -100),
    (100, 0, -1), (111, 0, -2), (100, 99, -1), (101, 100, -1),
    (101, 10, -10), (101, 1, -10), (111, 11, -11),
    # arr[x:-x:x]
    (0, -20, 1), (0, -20, 2), (0, -20, 10), (0, -20, 20), (0, -20, 21),
    (20, -50, 1), (20, -50, 10), (20, -50, 100),
    (0, -100, 1), (0, -111, 2), (1, -1, 1), (99, -100, 1), (100, -100, 1), (100, -101, 1),
    (101, -101, 1), (10, -101, 10), (1, -101, 10), (11, -111, 11),

    (50, -20, 1), (50, -20, 10), (50, -20, 100),
    (100, -99, 1), (101, -100, 1),
    (101, -10, 10), (101, -1, 10), (111, -11, 11),
    # arr[-x:x:x]
    (-20, 90, 1), (-20, 90, 10), (-20, 90, 100),
    (-1, 1, 1), (-99, 100, 1), (-100, 100, 1), (-100, 101, 1),
    (-101, 101, 1), (-10, 101, 10), (-1, 101, 10), (-11, 111, 11),

    (-20, 0, 1), (-20, 0, 2), (-20, 0, 10), (-20, 0, 20), (-20, 0, 21),
    (-50, 20, 1), (-50, 20, 10), (-50, 20, 100),
    (-100, 0, 1), (-111, 0, 2), (-100, 99, 1), (-101, 100, 1),
    (-101, 10, 10), (-101, 1, 10), (-111, 11, 11),
    # arr[x:-x:-x]
    (0, -20, -1), (0, -20, -2), (0, -20, -10), (0, -20, -20), (0, -20, -21),
    (20, -50, -1), (20, -50, -10), (20, -50, -100),
    (0, -100, -1), (0, -111, -2), (1, -1, -1), (99, -100, -1), (100, -100, -1), (100, -101, -1),
    (101, -101, -1), (10, -101, -10), (1, -101, -10), (11, -111, -11),

    (50, -20, -1), (50, -20, -10), (50, -20, -100),
    (100, -99, -1), (101, -100, -1),
    (101, -10, -10), (101, -1, -10), (111, -11, -11),
    # arr[-x:x:-x]
    (-20, 90, -1), (-20, 90, -10), (-20, 90, -100),
    (-1, 1, -1), (-99, 100, -1), (-100, 100, -1), (-100, 101, -1),
    (-101, 101, -1), (-10, 101, -10), (-1, 101, -10), (-11, 111, -11),

    (-20, 0, -1), (-20, 0, -2), (-20, 0, -10), (-20, 0, -20), (-20, 0, -21),
    (-50, 20, -1), (-50, 20, -10), (-50, 20, -100),
    (-100, 0, -1), (-111, 0, -2), (-100, 99, -1), (-101, 100, -1),
    (-101, 10, -10), (-101, 1, -10), (-111, 11, -11),
    # arr[-x:-x:x]
    (-20, -50, 1), (-20, -50, 10), (-20, -50, 100),
    (-1, -1, 1), (-99, -100, 1), (-100, -100, 1), (-100, -101, 1),
    (-101, -101, 1), (-10, -101, 10), (-1, -101, 10), (-11, -111, 11),

    (-50, -20, 1), (-50, -20, 10), (-50, -20, 100),
    (-100, -99, 1), (-101, -100, 1),
    (-101, -10, 10), (-101, -1, 10), (-111, -11, 11),
    # arr[-x:-x:-x]
    (-20, -50, -1), (-20, -50, -10), (-20, -50, -100),
    (-1, -1, -1), (-99, -100, -1), (-100, -100, -1), (-100, -101, -1),
    (-101, -101, -1), (-10, -101, -10), (-1, -101, -10), (-11, -111, -11),

    (-50, -20, -1), (-50, -20, -10), (-50, -20, -100),
    (-100, -99, -1), (-101, -100, -1),
    (-101, -10, -10), (-101, -1, -10), (-111, -11, -11),
]


def generate_random_slice(index_range: typing.Tuple[int, int],
                          stride_range: typing.Tuple[int, int],
                          is_start_None=False,
                          is_end_None=False,
                          is_stride_None=False) -> slice:
    """ generate a random slice for testing
    :param index_range: a tuple (x, y), where start value and end value will be selected between [x, y] randomly
    :param stride_range: a tuple (x, y), where stride value will be selected between [x, y] randomly
    :param is_start_None: a boolean value, if it is True, the start value will be None;
     otherwise, it will be selected randomly according to index_range.
    :param is_end_None: a boolean value, if it is True, the end value will be None;
     otherwise, it will be selected randomly according to index_range.
    :param is_stride_None: a boolean value, if it is True, the stride value will be None;
     otherwise, it will be selected randomly according to index_range.
    :return: a slice made from the start, end and stride selected according to the above parameters
    """
    start = None
    if not is_start_None:
        start = random.randint(*index_range)

    end = None
    if not is_end_None:
        end = random.randint(*index_range)

    stride = None
    if not is_stride_None:
        stride = 0
        while stride == 0:
            stride = random.randint(*stride_range)

    return slice(start, end, stride)


def calc_slice_len(slice_: slice, seq_len: int) -> int:
    """ Calculate the actual length of given slice.
    """
    start, stop, stride = slice_.indices(seq_len)
    return max(0, math.ceil((stop - start) / stride))
