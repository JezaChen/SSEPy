# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
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


if __name__ == '__main__':
    test_db = {
        b"a": [1, 2, 3, 4, 6],
        b"b": [1, 4, 5, 6, 7],
        b"c": [1, 2, 3, 9, 11]
    }
    print(get_total_size(test_db))
    print(get_distinct_keyword_count(test_db))
    print(get_distinct_file_count(test_db))
