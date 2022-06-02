# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: test_DP17_Pi.py
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import unittest

import schemes.DP17.Pi.config
from schemes.DP17.Pi.config import PiConfig
from schemes.DP17.Pi.construction import Pi
from schemes.DP17.Pi.structures import PiKey, PiToken, PiEncryptedDatabase, PiResult
from test.tools.faker import fake_db_for_inverted_index_based_sse

TEST_KEYWORD_SIZE = 16


class TestPi(unittest.TestCase):

    def test_method_correctness_simple_version(self):
        db = {
            b"China": [b"12345678", b"23221233", b"23421232"],
            b"Ukraine":
            [b"\x00\x00az\x02\x03sc", b"\x00\x00\x00\x00\x01\x00\x02\x01"]
        }

        config_dict = schemes.DP17.Pi.config.DEFAULT_CONFIG

        scheme = Pi(config_dict)
        key = scheme._Gen()

        encrypted_index = scheme._Enc(key, db)
        token = scheme._Trap(key, b"China")
        result = scheme._Search(encrypted_index, token)
        self.assertEqual(set(db[b"China"]), result.result)

    def test_method_correctness(self):
        keyword_count = 1000

        config_dict = schemes.DP17.Pi.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(
            TEST_KEYWORD_SIZE,
            config_dict.get("param_identifier_size"),
            keyword_count,
            db_w_size_range=(1, 200))

        scheme = Pi(config_dict)
        key = scheme._Gen()

        encrypted_index = scheme._Enc(key, db)
        for keyword in db:
            token = scheme._Trap(key, keyword)
            result = scheme._Search(encrypted_index, token)
            self.assertEqual(set(db[keyword]), result.result)

    def test_interface_correctness(self):
        keyword_count = 1000

        config_dict = schemes.DP17.Pi.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(
            TEST_KEYWORD_SIZE,
            config_dict.get("param_identifier_size"),
            keyword_count,
            db_w_size_range=(1, 200))

        scheme = Pi(config_dict)
        key = scheme.KeyGen()
        encrypted_index = scheme.EDBSetup(key, db)
        for keyword in db:
            token = scheme.TokenGen(key, keyword)
            result = scheme.Search(encrypted_index, token)
            self.assertEqual(set(db[keyword]), result.result)

    def test_module_loader(self):
        loader = schemes.load_sse_module("DP17.Pi")
        self.assertEqual(loader.SSEScheme, Pi)
        self.assertEqual(loader.SSEConfig, PiConfig)
        self.assertEqual(loader.SSEKey, PiKey)
        self.assertEqual(loader.SSEToken, PiToken)
        self.assertEqual(loader.SSEEncryptedDatabase, PiEncryptedDatabase)
        self.assertEqual(loader.SSEResult, PiResult)

    def test_structure_serialization(self):
        keyword_count = 10

        config_dict = schemes.DP17.Pi.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(
            TEST_KEYWORD_SIZE,
            config_dict.get("param_identifier_size"),
            keyword_count,
            db_w_size_range=(1, 200))

        scheme = Pi(config_dict)
        key = scheme.KeyGen()
        self.assertEqual(key, PiKey.deserialize(key.serialize(),
                                                scheme.config))

        encrypted_index = scheme.EDBSetup(key, db)
        self.assertEqual(
            encrypted_index,
            PiEncryptedDatabase.deserialize(encrypted_index.serialize(),
                                            scheme.config))

        for keyword in db:
            token = scheme.TokenGen(key, keyword)
            self.assertEqual(
                token, PiToken.deserialize(token.serialize(), scheme.config))
            result = scheme.Search(encrypted_index, token)
            self.assertEqual(
                result, PiResult.deserialize(result.serialize(),
                                             scheme.config))

            self.assertEqual(set(db[keyword]), result.result)
