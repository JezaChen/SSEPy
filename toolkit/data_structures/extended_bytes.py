# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: extended_bytes.py 
@time: 2022/05/07
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import operator
from collections.abc import Sequence


class ExtendedBytes(Sequence):
    """ Extended Version of bytes
    """

    def __init__(self, original_bytes: bytes):
        self.__original_bytes = bytes(original_bytes)  # initialize __original_bytes from bytes(...)

    def __getitem__(self, key):
        if isinstance(key, slice):
            cls = type(self)
            return cls(self.__original_bytes[key])  # build another ExtendedBytes
        index = operator.index(key)
        return self.__original_bytes[index]

    def __len__(self):
        return len(self.__original_bytes)

    def __getattr__(self, item):
        return getattr(self.__original_bytes, item)

    def __iter__(self):
        return iter(self.__original_bytes)

    def __repr__(self) -> str:
        class_name = type(self).__name__
        return '{}({})'.format(class_name, self.__original_bytes)

    def __eq__(self, other):
        if isinstance(other, ExtendedBytes):
            return self.__original_bytes == other.__original_bytes
        else:
            return NotImplemented

    def concat(self, o):
        print("concat")
