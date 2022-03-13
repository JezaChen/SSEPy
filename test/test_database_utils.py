# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: test_database_utils.py 
@time: 2022/03/13
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import os
import unittest

from toolkit.database_utils import parse_identifiers_from_block_given_identifier_size, partition_identifiers_to_blocks


def fake_identifiers(identifier_size: int, identifier_count: int) -> list:
    return [os.urandom(identifier_size) for _ in range(identifier_count)]


class TestDatabaseUtils(unittest.TestCase):
    def test_identifiers_partition(self):
        identifier_count = 2000
        identifier_size = 8
        identifier_count_in_one_block = 64

        identifier_list = fake_identifiers(identifier_size, identifier_count)
        block_list = list(
            partition_identifiers_to_blocks(identifier_list, identifier_count_in_one_block, identifier_size))

        parse_result = []
        for block in block_list:
            parse_result.extend(parse_identifiers_from_block_given_identifier_size(block, identifier_size))
        self.assertListEqual(identifier_list, parse_result)

    def test_identifiers_partition_given_block_size(self):
        identifier_count = 2000
        identifier_size = 8
        identifier_count_in_one_block = 64
        block_size = identifier_count_in_one_block * identifier_size + 2

        identifier_list = fake_identifiers(identifier_size, identifier_count)
        block_list = list(
            partition_identifiers_to_blocks(identifier_list, identifier_count_in_one_block, identifier_size,
                                            block_size_bytes=block_size))

        parse_result = []
        for block in block_list:
            parse_result.extend(parse_identifiers_from_block_given_identifier_size(block, identifier_size))
        self.assertListEqual(identifier_list, parse_result)
