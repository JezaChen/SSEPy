# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: bytes_utils.py 
@time: 2022/03/09
@contact: jeza@vip.qq.com
@software: PyCharm 
@description: Collection of tools for byte manipulation
"""


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
