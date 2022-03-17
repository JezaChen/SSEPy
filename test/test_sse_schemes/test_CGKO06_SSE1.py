# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: test_CGKO06_SSE1.py
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import unittest

import schemes.CGKO06.SSE1.config
from schemes.CGKO06.SSE1.config import SSE1Config
from schemes.CGKO06.SSE1.construction import SSE1
from schemes.CGKO06.SSE1.structures import SSE1Key, SSE1Token, SSE1EncryptedDatabase, SSE1Result
from test.tools import fake_db_for_inverted_index_based_sse


class TestSSE1(unittest.TestCase):
    def test_method_correctness_simple_version(self):
        db = {
            b"China": [b'\xc0\x80\xbd\xe2\x1c\xb0v\xb9',
                       b'@\r\x88\xfc\x0f=\x12=',
                       b'o\x82\x17\xbd\x9cG\xef\xd4',
                       b'\xc3\x9f\xcc8\x93Dp\xeb',
                       b'P8>\xd5,S\t\x83',
                       b'\x9e\x06\xe3\xf5Z\xd76\xbc',
                       b'\x9a\xe4\xc2\xb7\xab7\x7fs'],
            b"Ukraine": [b'\xc0\x80\xbd\xe2\x1c\xb0v\xb9',
                         b'@\r\x88\xfc\x0f=\x12=',
                         b'o\x82\x17\xbd\x9cG\xef\xd4',
                         b'\xc3\x9f\xcc8\x93Dp\xeb',
                         b'P8>\xd5,S\t\x83',
                         b'\x9e\x06\xe3\xf5Z\xd76\xbc',
                         b'\x9a\xe4\xc2\xb7\xab7\x7fs']
        }

        config_dict = schemes.CGKO06.SSE1.config.DEFAULT_CONFIG

        scheme = SSE1(config_dict)
        key = scheme._Gen()

        encrypted_index = scheme._Enc(key, db)
        token = scheme._Trap(key, b"China")
        result = scheme._Search(encrypted_index, token)
        self.assertEqual(db[b"China"], result.result)

    def test_method_correctness(self):
        keyword_count = 1000

        config_dict = schemes.CGKO06.SSE1.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(config_dict["param_l"],
                                                  config_dict["param_identifier_size"],
                                                  keyword_count, db_w_size_range=(1, 100))

        scheme = SSE1(config_dict)
        key = scheme._Gen()

        encrypted_index = scheme._Enc(key, db)
        for keyword in db:
            token = scheme._Trap(key, keyword)
            result = scheme._Search(encrypted_index, token)
            self.assertEqual(db[keyword], result.result)

    def test_interface_correctness(self):
        keyword_count = 1000

        config_dict = schemes.CGKO06.SSE1.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(config_dict["param_l"],
                                                  config_dict["param_identifier_size"],
                                                  keyword_count, db_w_size_range=(1, 100))

        scheme = SSE1(config_dict)
        key = scheme.KeyGen()
        encrypted_index = scheme.EDBSetup(key, db)
        for keyword in db:
            token = scheme.TokenGen(key, keyword)
            result = scheme.Search(encrypted_index, token)
            self.assertEqual(db[keyword], result.result)

    def test_module_loader(self):
        loader = schemes.load_sse_module("CGKO06.SSE1")
        self.assertEqual(loader.SSEScheme, SSE1)
        self.assertEqual(loader.SSEConfig, SSE1Config)
        self.assertEqual(loader.SSEKey, SSE1Key)
        self.assertEqual(loader.SSEToken, SSE1Token)
        self.assertEqual(loader.SSEEncryptedDatabase, SSE1EncryptedDatabase)
        self.assertEqual(loader.SSEResult, SSE1Result)
