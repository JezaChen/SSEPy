# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: bits_utils.py 
@time: 2022/03/11
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import typing

from toolkit.bits import Bitset


def half_bits(xbits: typing.Union[int, Bitset]) -> (Bitset, Bitset):
    """Get the first half of xbits and the second half of bits,
    where the length of the two bits are (len(xbits) + 1) // 2
    """
    if isinstance(xbits, int):
        xbits = Bitset(xbits)

    half_len = (len(xbits) + 1) // 2
    right_half = xbits.get_lower_bits(half_len)
    left_half = xbits.get_higher_bits(len(xbits) - half_len)
    if len(left_half) < half_len:  # half_len - 1
        left_half.length = half_len

    return left_half, right_half


def half_bits_not_padding(xbits: typing.Union[int, Bitset]) -> (Bitset, Bitset):
    """Get the first half of xbits and the second half of bits,
    where the length of the two bits are not equal when len(xbits) % 2 == 1
    """
    if isinstance(xbits, int):
        xbits = Bitset(xbits)

    half_len = (len(xbits) + 1) // 2
    right_half = xbits.get_lower_bits(half_len)
    left_half = xbits.get_higher_bits(len(xbits) - half_len)

    return left_half, right_half
