# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: test_CJJ14_PiPtr.py
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import unittest

import schemes.CJJ14.PiPtr.config
from schemes.CJJ14.PiPtr.config import PiPtrConfig
from schemes.CJJ14.PiPtr.construction import PiPtr
from schemes.CJJ14.PiPtr.structures import PiPtrKey, PiPtrToken, PiPtrEncryptedDatabase, PiPtrResult
from test.tools import fake_db_for_inverted_index_based_sse

TEST_KEYWORD_SIZE = 16


class TestPiPtr(unittest.TestCase):

    def test_method_correctness_simple_version(self):
        db = {
            b"China": [b"12345678", b"23221233", b"23421232"],
            b"Ukraine":
            [b"\x00\x00az\x02\x03sc", b"\x00\x00\x00\x00\x01\x00\x02\x01"]
        }

        config_dict = schemes.CJJ14.PiPtr.config.DEFAULT_CONFIG

        scheme = PiPtr(config_dict)
        key = scheme._Gen()

        encrypted_index = scheme._Enc(key, db)
        token = scheme._Trap(key, b"China")
        result = scheme._Search(encrypted_index, token)
        self.assertEqual(db[b"China"], result.result)

    def test_method_correctness(self):
        keyword_count = 1000

        config_dict = schemes.CJJ14.PiPtr.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(
            TEST_KEYWORD_SIZE,
            config_dict.get("param_identifier_size"),
            keyword_count,
            db_w_size_range=(1, 200))

        scheme = PiPtr(config_dict)
        key = scheme._Gen()

        encrypted_index = scheme._Enc(key, db)
        for keyword in db:
            token = scheme._Trap(key, keyword)
            result = scheme._Search(encrypted_index, token)
            self.assertEqual(db[keyword], result.result)

    def test_interface_correctness(self):
        keyword_count = 1000

        config_dict = schemes.CJJ14.PiPtr.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(
            TEST_KEYWORD_SIZE,
            config_dict.get("param_identifier_size"),
            keyword_count,
            db_w_size_range=(1, 200))

        scheme = PiPtr(config_dict)
        key = scheme.KeyGen()
        encrypted_index = scheme.EDBSetup(key, db)
        for keyword in db:
            token = scheme.TokenGen(key, keyword)
            result = scheme.Search(encrypted_index, token)
            self.assertEqual(db[keyword], result.result)

    def test_module_loader(self):
        loader = schemes.load_sse_module("CJJ14.PiPtr")
        self.assertEqual(loader.SSEScheme, PiPtr)
        self.assertEqual(loader.SSEConfig, PiPtrConfig)
        self.assertEqual(loader.SSEKey, PiPtrKey)
        self.assertEqual(loader.SSEToken, PiPtrToken)
        self.assertEqual(loader.SSEEncryptedDatabase, PiPtrEncryptedDatabase)
        self.assertEqual(loader.SSEResult, PiPtrResult)

    def test_structure_serialization(self):
        keyword_count = 10

        config_dict = schemes.CJJ14.PiPtr.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(
            TEST_KEYWORD_SIZE,
            config_dict.get("param_identifier_size"),
            keyword_count,
            db_w_size_range=(1, 200))

        scheme = PiPtr(config_dict)
        key = scheme.KeyGen()
        self.assertEqual(key,
                         PiPtrKey.deserialize(key.serialize(), scheme.config))

        encrypted_index = scheme.EDBSetup(key, db)
        self.assertEqual(
            encrypted_index,
            PiPtrEncryptedDatabase.deserialize(encrypted_index.serialize(),
                                               scheme.config))

        for keyword in db:
            token = scheme.TokenGen(key, keyword)
            self.assertEqual(
                token, PiPtrToken.deserialize(token.serialize(),
                                              scheme.config))
            result = scheme.Search(encrypted_index, token)
            self.assertEqual(
                result,
                PiPtrResult.deserialize(result.serialize(), scheme.config))

            self.assertEqual(db[keyword], result.result)
