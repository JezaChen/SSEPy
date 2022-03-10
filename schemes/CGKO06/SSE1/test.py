# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: test.py 
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import unittest

import schemes.CGKO06.SSE1.param
from schemes.CGKO06.SSE1.construction import SSE1
from toolkit.test_utils import fake_db_for_inverted_index_based_sse


class TestSSE1(unittest.TestCase):
    def test_method_correctness_simple_version(self):
        scheme = SSE1()
        key = scheme._Gen()
        db = {
            b"China": [b"12345678", b"23221233", b"23421232"],
            b"Ukraine": [b"\x00\x00az\x02\x03sc", b"\x00\x00\x00\x00\x01\x00\x02\x01"]
        }
        encrypted_index = scheme._Enc(key, db)
        token = scheme._Trap(key, b"China")
        result = scheme._Search(encrypted_index, token)
        self.assertEqual(db[b"China"], result)

    def test_method_correctness(self):
        keyword_count = 100

        scheme = SSE1()
        key = scheme._Gen()
        db = fake_db_for_inverted_index_based_sse(schemes.CGKO06.SSE1.param.param_l,
                                                  schemes.CGKO06.SSE1.param.param_identifier_size,
                                                  keyword_count)
        encrypted_index = scheme._Enc(key, db)
        for keyword in db:
            token = scheme._Trap(key, keyword)
            result = scheme._Search(encrypted_index, token)
            self.assertEqual(db[keyword], result)

    def test_interface_correctness(self):
        keyword_count = 100

        scheme = SSE1()
        key = scheme.KeyGen()
        db = fake_db_for_inverted_index_based_sse(schemes.CGKO06.SSE1.param.param_l,
                                                  schemes.CGKO06.SSE1.param.param_identifier_size,
                                                  keyword_count)
        encrypted_index = scheme.EDBSetup(key, db)
        for keyword in db:
            token = scheme.TokenGen(key, keyword)
            result = scheme.Search(encrypted_index, token)
            self.assertEqual(db[keyword], result.result)
