# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: test_CJJ14_Pi2Lev.py
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import unittest

import schemes.CJJ14.Pi2Lev.config
from schemes.CJJ14.Pi2Lev.config import Pi2LevConfig
from schemes.CJJ14.Pi2Lev.construction import Pi2Lev
from schemes.CJJ14.Pi2Lev.structures import Pi2LevKey, Pi2LevToken, Pi2LevEncryptedDatabase, Pi2LevResult
from test.tools import fake_db_for_inverted_index_based_sse

TEST_KEYWORD_SIZE = 16


class TestPi2Lev(unittest.TestCase):
    def test_method_correctness_simple_version(self):
        db = {
            b"China": [b"12345678", b"23221233", b"23421232"],
            b"Ukraine": [b"\x00\x00az\x02\x03sc", b"\x00\x00\x00\x00\x01\x00\x02\x01"]
        }

        config_dict = schemes.CJJ14.Pi2Lev.config.DEFAULT_CONFIG

        scheme = Pi2Lev(config_dict)
        key = scheme._Gen()

        encrypted_index = scheme._Enc(key, db)
        token = scheme._Trap(key, b"China")
        result = scheme._Search(encrypted_index, token)
        self.assertEqual(db[b"China"], result.result)

    def test_method_correctness(self):
        keyword_count = 1000

        config_dict = schemes.CJJ14.Pi2Lev.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(TEST_KEYWORD_SIZE,
                                                  config_dict.get("param_identifier_size"),
                                                  keyword_count,
                                                  db_w_size_range=(1, 200))

        scheme = Pi2Lev(config_dict)
        key = scheme._Gen()

        encrypted_index = scheme._Enc(key, db)
        for keyword in db:
            token = scheme._Trap(key, keyword)
            result = scheme._Search(encrypted_index, token)
            self.assertEqual(db[keyword], result.result)

    def test_interface_correctness(self):
        keyword_count = 1000

        config_dict = schemes.CJJ14.Pi2Lev.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(TEST_KEYWORD_SIZE,
                                                  config_dict.get("param_identifier_size"),
                                                  keyword_count,
                                                  db_w_size_range=(1, 200))

        scheme = Pi2Lev(config_dict)
        key = scheme.KeyGen()
        encrypted_index = scheme.EDBSetup(key, db)
        for keyword in db:
            token = scheme.TokenGen(key, keyword)
            result = scheme.Search(encrypted_index, token)
            self.assertEqual(db[keyword], result.result)

    def test_module_loader(self):
        loader = schemes._load_sse_module("CJJ14.Pi2Lev")
        self.assertEqual(loader.SSEScheme, Pi2Lev)
        self.assertEqual(loader.SSEConfig, Pi2LevConfig)
        self.assertEqual(loader.SSEKey, Pi2LevKey)
        self.assertEqual(loader.SSEToken, Pi2LevToken)
        self.assertEqual(loader.SSEEncryptedDatabase, Pi2LevEncryptedDatabase)
        self.assertEqual(loader.SSEResult, Pi2LevResult)
