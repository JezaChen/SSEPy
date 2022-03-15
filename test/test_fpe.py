# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: test_fpe.py 
@time: 2022/03/12
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import unittest

from test.tools import generate_random_bitset
from toolkit.symmetric_encryption.fpe import BitwiseFFX


class TestFPE(unittest.TestCase):
    def test_fpe_correctness(self):
        fpe = BitwiseFFX()
        keys = [
            b"JezaChen",
            b"Sun yat-sen university",
            b"\x00\xff\x01abccjkj\x11"
        ]
        test_num_per_bit_len = 20
        bit_len_to_test = [10, 20, 21, 40, 43, 50, 100, 200, 1024, 1033, 2047, 2048]
        for key in keys:
            for bit_len in bit_len_to_test:
                for _ in range(test_num_per_bit_len):
                    xbits = generate_random_bitset(bit_len)
                    self.assertEqual(fpe.decrypt(key, fpe.encrypt(key, xbits)), xbits)
