# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: test_CGKO06_SSE2.py
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import unittest

import schemes.CGKO06.SSE2.config
from schemes.CGKO06.SSE2.config import SSE2Config
from schemes.CGKO06.SSE2.construction import SSE2
from schemes.CGKO06.SSE2.structures import SSE2Token, SSE2EncryptedDatabase, SSE2Result, SSE2Key
from test.tools.faker import fake_db_for_inverted_index_based_sse


class TestSSE2(unittest.TestCase):

    def test_method_correctness_simple_version(self):
        db = {
            b"China": [b"12345678", b"23221233", b"23421232"],
            b"Ukraine":
                [b"\x00\x00az\x02\x03sc", b"\x00\x00\x00\x00\x01\x00\x02\x01"]
        }

        config_dict = schemes.CGKO06.SSE2.config.DEFAULT_CONFIG
        schemes.CGKO06.SSE2.config.scan_database_and_update_config_dict(
            config_dict, database=db)

        scheme = SSE2(config_dict)
        key = scheme._Gen()

        encrypted_index = scheme._Enc(key, db)
        token = scheme._Trap(key, b"China")
        result = scheme._Search(encrypted_index, token)
        self.assertEqual(db[b"China"], result.result)

    def test_method_correctness(self):
        keyword_count = 100

        config_dict = schemes.CGKO06.SSE2.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(
            config_dict["param_l"], config_dict["param_identifier_size"],
            keyword_count)

        schemes.CGKO06.SSE2.config.scan_database_and_update_config_dict(
            config_dict, database=db)

        scheme = SSE2(config_dict)
        key = scheme._Gen()

        encrypted_index = scheme._Enc(key, db)
        for keyword in db:
            token = scheme._Trap(key, keyword)
            result = scheme._Search(encrypted_index, token)
            self.assertEqual(db[keyword], result.result)

    def test_interface_correctness(self):
        keyword_count = 100

        config_dict = schemes.CGKO06.SSE2.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(
            config_dict["param_l"], config_dict["param_identifier_size"],
            keyword_count)

        schemes.CGKO06.SSE2.config.scan_database_and_update_config_dict(
            config_dict, database=db)

        scheme = SSE2(config_dict)
        key = scheme.KeyGen()
        encrypted_index = scheme.EDBSetup(key, db)
        for keyword in db:
            token = scheme.TokenGen(key, keyword)
            result = scheme.Search(encrypted_index, token)
            self.assertEqual(db[keyword], result.result)

    def test_module_loader(self):
        loader = schemes.load_sse_module("CGKO06.SSE2")
        self.assertEqual(loader.SSEScheme, SSE2)
        self.assertEqual(loader.SSEConfig, SSE2Config)
        self.assertEqual(loader.SSEKey, SSE2Key)
        self.assertEqual(loader.SSEToken, SSE2Token)
        self.assertEqual(loader.SSEEncryptedDatabase, SSE2EncryptedDatabase)
        self.assertEqual(loader.SSEResult, SSE2Result)

    def test_structure_serialization(self):
        keyword_count = 10

        config_dict = schemes.CGKO06.SSE2.config.DEFAULT_CONFIG

        db = fake_db_for_inverted_index_based_sse(
            config_dict["param_l"], config_dict["param_identifier_size"],
            keyword_count)
        schemes.CGKO06.SSE2.config.scan_database_and_update_config_dict(
            config_dict, database=db)

        scheme = SSE2(config_dict)
        key = scheme.KeyGen()
        self.assertEqual(key, SSE2Key.deserialize(key.serialize(), scheme.config))

        encrypted_index = scheme.EDBSetup(key, db)
        self.assertEqual(encrypted_index,
                         SSE2EncryptedDatabase.deserialize(encrypted_index.serialize(), scheme.config))

        for keyword in db:
            token = scheme.TokenGen(key, keyword)
            self.assertEqual(token,
                             SSE2Token.deserialize(token.serialize(),
                                                   scheme.config))
            result = scheme.Search(encrypted_index, token)
            self.assertEqual(result,
                             SSE2Result.deserialize(result.serialize(),
                                                    scheme.config))

            self.assertEqual(db[keyword], result.result)
