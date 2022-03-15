# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: structures.py 
@time: 2022/03/10
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import abc
from schemes.interface.objects import SSEObject


class SSEKey(SSEObject, metaclass=abc.ABCMeta):
    pass


class SSEEncryptedDatabase(SSEObject, metaclass=abc.ABCMeta):
    pass


class SSEToken(SSEObject, metaclass=abc.ABCMeta):
    pass


class SSEResult(SSEObject, metaclass=abc.ABCMeta):
    pass
