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


class SSEObject(metaclass=abc.ABCMeta):
    def serialize(self) -> bytes:
        pass

    @classmethod
    def deserialize(cls, xbytes: bytes):
        pass
