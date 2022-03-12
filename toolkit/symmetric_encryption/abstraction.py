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
@description: 
"""
import abc


class AbstractSymmetricEncryption(metaclass=abc.ABCMeta):
    def __init__(self, *, cipher_length: int, key_length: int, message_length: int):
        self.cipher_length = cipher_length
        self.key_length = key_length
        self.message_length = message_length

    def KeyGen(self) -> bytes:
        pass

    def Encrypt(self, key: bytes, message: bytes) -> bytes:
        pass

    def Decrypt(self, key: bytes, cipher_text: bytes) -> bytes:
        pass
