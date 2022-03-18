# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: database_utils.py 
@time: 2022/03/11
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description:
Database related utility functions,
such as getting the number of individual keywords, database size, etc.
"""


def get_total_size(db: dict):
    return sum(len(identifier_list) for identifier_list in db.values())


def get_distinct_keyword_count(db: dict):
    return len(db)


def get_distinct_file_count(db: dict):
    file_set = set()
    for identifier_list in db.values():
        file_set.update(identifier_list)
    return len(file_set)


def partition_identifiers_to_blocks(identifier_list: list,
                                    entry_count_in_one_block: int,
                                    identifier_size: int,
                                    block_size_bytes: int = 0):
    if block_size_bytes == 0:
        block_size_bytes = entry_count_in_one_block * identifier_size

    if block_size_bytes < entry_count_in_one_block * identifier_size:
        raise ValueError(
            "parameter block_size_bytes should be greater than or equal to "
            "entry_count_in_one_block * identifier_size")

    for i in range(0, len(identifier_list), entry_count_in_one_block):
        block = b''.join(identifier_list[i:i + entry_count_in_one_block])
        if len(block) < block_size_bytes:
            block += b'\x00' * (block_size_bytes - len(block))
        yield block


def parse_identifiers_from_block_given_identifier_size(block: bytes,
                                                       identifier_size: int):
    result = []
    for i in range(0, len(block), identifier_size):
        identifier = block[i:i + identifier_size]
        if identifier == b'\x00' * len(identifier):
            break
        result.append(identifier)
    return result


def parse_identifiers_from_block_given_entry_count_in_one_block(
        block: bytes, entry_count_in_one_block: int):
    identifier_size = len(block) // entry_count_in_one_block
    return parse_identifiers_from_block_given_identifier_size(
        block, identifier_size)


def convert_database_keyword_to_bytes(db: dict, encoding="utf-8"):
    """Make sure that all keywords in db are strings and all values are hex-strings. """
    result = {}
    for keyword in db:
        keyword_bytes = bytes(keyword, encoding=encoding)
        identifier_bytes_list = []
        for identifier in db[keyword]:
            identifier_bytes_list.append(bytes.fromhex(identifier))
        result[keyword_bytes] = identifier_bytes_list
    return result


if __name__ == '__main__':
    test_db = {
        b"a": [1, 2, 3, 4, 6],
        b"b": [1, 4, 5, 6, 7],
        b"c": [1, 2, 3, 9, 11]
    }
    print(get_total_size(test_db))
    print(get_distinct_keyword_count(test_db))
    print(get_distinct_file_count(test_db))
