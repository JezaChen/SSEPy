# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: abstraction.py 
@time: 2022/03/10
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import abc


class AbstractPRF(metaclass=abc.ABCMeta):

    def __init__(self, *, output_length: int, key_length: int,
                 message_length: int):
        self.output_length = output_length
        self.key_length = key_length
        self.message_length = message_length

    def __call__(self, key: bytes, message: bytes) -> bytes:
        raise NotImplementedError("Class AbstractPRF is an abstract class.")
