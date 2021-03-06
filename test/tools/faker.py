# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: tools.py
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import os
import random

from toolkit.bits import Bitset

__all__ = ["fake_db_for_inverted_index_based_sse", "generate_random_bitset"]


def fake_db_for_inverted_index_based_sse(fixed_keyword_size: int,
                                         fixed_file_id_size: int,
                                         distinct_keyword_count: int,
                                         db_w_size_range: tuple = (1, 10),
                                         ):
    """
    Generate a test database for inverted index-based SSE schemes
    Note that the sizes of keywords and file identifiers are fixed
    :param fixed_keyword_size: (bytes) the size of keyword
    :param fixed_file_id_size: (bytes) the size of file identifier
    :param distinct_keyword_count: the number of distinct keywords in the fake DB
    :param db_w_size_range: The size range of DB(w) corresponding to a single keyword, default value is [1, 10]
    :return:
    """
    db = {}
    for _ in range(distinct_keyword_count):
        keyword = os.urandom(fixed_keyword_size)
        db[keyword] = []
        for _ in range(random.randint(*db_w_size_range)):
            db[keyword].append(os.urandom(fixed_file_id_size))
    return db


def generate_random_bitset(bit_len):
    num = random.getrandbits(bit_len)
    return Bitset(num, length=bit_len)
