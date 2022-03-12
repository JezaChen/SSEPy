# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: objects.py 
@time: 2022/03/10
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""

import abc

from schemes.interface.config import SSEConfig


class SSEObject(metaclass=abc.ABCMeta):
    def __init__(self, config: SSEConfig):
        pass

    @abc.abstractmethod
    def serialize(self) -> bytes:
        pass

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, xbytes: bytes, config: SSEConfig):
        pass
