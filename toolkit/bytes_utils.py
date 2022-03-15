# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: bytes_utils.py 
@time: 2022/03/09
@contact: jeza@vip.qq.com
@software: PyCharm 
@description: Collection of tools for byte manipulation
"""
import itertools


def bytes_xor(a: bytes, b: bytes):
    """Bytes Xor Operation: a xor b"""
    result = bytearray(a)
    for i, b_byte in enumerate(b):
        result[i] ^= b_byte
    return bytes(result)


def int_to_bytes(x: int, output_len: int = -1) -> bytes:
    if output_len == -1:
        output_len = (x.bit_length() + 7) // 8
    return x.to_bytes(output_len, 'big')


def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')


def add_leading_zeros(xbytes: bytes, output_len: int):
    return b'\x00' * max(output_len - len(xbytes), 0) + xbytes


def split_bytes_given_slice_len(xbytes: bytes, slice_len_list: list) -> list:
    if len(xbytes) != sum(slice_len for slice_len in slice_len_list):
        raise ValueError("Length mismatch, please ensure that the length of xbytes is equal to "
                         "the sum of the individual values of slice_len_list")
    result = []
    c = 0
    slice_len_accumulation = itertools.accumulate(slice_len_list)
    while c != len(xbytes):
        next_c = next(slice_len_accumulation)
        result.append(xbytes[c: next_c])
        c = next_c
    return result
