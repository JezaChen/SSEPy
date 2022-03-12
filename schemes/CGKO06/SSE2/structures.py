# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: structures.py 
@time: 2022/03/11
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import pickle

from schemes.CGKO06.SSE2.config import SSE2_HEADER, SSE2Config
from schemes.interface.structures import SSEKey, SSEEncryptedDatabase, SSEToken, SSEResult


class SSE2Key(SSEKey):
    __slots__ = ["K1", "K2"]

    def __init__(self, K1: bytes, K2: bytes, config: SSE2Config = None):
        super(SSE2Key, self).__init__(config)
        self.K1, self.K2 = K1, K2

    def serialize(self) -> bytes:
        return b''.join([self.K1, self.K2])

    @classmethod
    def deserialize(cls, xbytes: bytes, config: SSE2Config):
        if len(xbytes) != 2 * config.param_k:
            raise ValueError("The length of xbytes must be 2 times the length of the parameter param_k.")

        key_list = [xbytes[i: i + config.param_k] for i in range(0, len(xbytes), config.param_k)]
        return cls(*key_list)


class SSE2EncryptedDatabase(SSEEncryptedDatabase):
    __slots__ = ["I"]  # dict I

    def __init__(self, I: dict, config: SSE2Config = None):
        super(SSE2EncryptedDatabase, self).__init__(config)
        self.I = I

    def serialize(self) -> bytes:
        data = SSE2_HEADER + pickle.dumps(self.I)
        return data

    @classmethod
    def deserialize(cls, xbytes: bytes, config: SSE2Config = None):
        if xbytes[:len(SSE2_HEADER)] != SSE2_HEADER:
            raise ValueError("Parse header error.")

        data_bytes = xbytes[len(SSE2_HEADER):]
        I = pickle.loads(data_bytes)
        return cls(I)


class SSE2Token(SSEToken):
    __slots__ = ["t"]  # array t

    def __init__(self, t: list, config: SSE2Config = None):
        super(SSE2Token, self).__init__(config)
        self.t = t

    def serialize(self) -> bytes:
        return pickle.dumps(self.t)

    @classmethod
    def deserialize(cls, xbytes: bytes, config: SSE2Config = None):
        t = pickle.loads(xbytes)
        if not isinstance(t, list):
            return ValueError("The data contained in xbytes is not a list.")
        return cls(t, config)


class SSE2Result(SSEResult):
    __slots__ = ["result"]

    def __init__(self, result: list, config: SSE2Config = None):
        super(SSE2Result, self).__init__(config)
        self.result = result

    def serialize(self) -> bytes:
        return pickle.dumps(self.result)

    @classmethod
    def deserialize(cls, xbytes: bytes, config: SSE2Config = None):
        result = pickle.loads(xbytes)
        if not isinstance(result, list):
            return ValueError("The data contained in xbytes is not a list.")

        return cls(result, config)
