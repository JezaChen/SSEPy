# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: abstraction.py 
@time: 2022/03/10
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm
"""
import abc


class AbstractPRP(metaclass=abc.ABCMeta):
    def __init__(self, *, message_length: int, key_length: int):
        self.key_length = key_length
        self.message_length = message_length

    def __call__(self, key: bytes, message: bytes) -> bytes:
        raise NotImplementedError("Class AbstractPRP is an abstract class.")

