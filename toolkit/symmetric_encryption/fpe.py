# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: fpe.py 
@time: 2022/03/11
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: Format-preserving encryption: bitwise version
See https://github.com/emulbreh/pyffx (MIT License)
"""
import hashlib
import hmac
import struct

from toolkit.bits import Bitset
from toolkit.bits_utils import half_bits, half_bits_not_padding

DEFAULT_ROUNDS = 10


class BitwiseFFX:
    """ Format-preserving, Feistel-based encryption (FFX)
    See https://github.com/emulbreh/pyffx
    For performance reasons, we only implement the binary version of this
    """

    def __init__(self, rounds=DEFAULT_ROUNDS, digest_mod=hashlib.sha1):
        self.rounds = rounds
        self.digest_mod = digest_mod
        self.digest_size = self.digest_mod().digest_size

    def round(self, key: bytes, i: int, s: Bitset, output_len=0) -> Bitset:
        if output_len == 0:
            output_len = len(s)

        pre = struct.pack('I%sI' % len(s), i, *s)
        output_len_per_hash = int(self.digest_size * 8)
        i = 0
        result = Bitset(0b0, 0)
        while True:
            h = hmac.new(key, pre + struct.pack('I', i), self.digest_mod)
            d = Bitset(int(h.hexdigest(), 16), output_len_per_hash)
            result = result + d
            if len(result) >= output_len:
                break

        return result.get_higher_bits(output_len)

    def split(self, v: Bitset) -> (Bitset, Bitset):
        return half_bits_not_padding(v)

    def encrypt(self, key: bytes, v: Bitset) -> Bitset:
        a, b = self.split(v)
        for i in range(self.rounds):
            c = a ^ self.round(key, i, b, len(a))
            a, b = b, c
        return a + b

    def decrypt(self, key: bytes, v: Bitset) -> Bitset:
        a, b = self.split(v)
        for i in range(self.rounds - 1, -1, -1):
            b, c = a, b
            a = c ^ self.round(key, i, b, len(c))
        return a + b
