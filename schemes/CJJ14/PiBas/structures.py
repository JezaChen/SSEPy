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

from schemes.CJJ14.PiBas.config import PiBasConfig, PI_BAS_HEADER
from schemes.interface.structures import SSEKey, SSEEncryptedDatabase, SSEToken, SSEResult


class PiBasKey(SSEKey):
    __slots__ = ["K"]

    def __init__(self, K: bytes, config: PiBasConfig = None):
        super(PiBasKey, self).__init__(config)
        self.K = K

    def serialize(self) -> bytes:
        return self.K

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiBasConfig):
        if len(xbytes) != config.param_lambda:
            raise ValueError("The length of xbytes must be the same as the length of the parameter param_k.")

        return cls(xbytes)


class PiBasEncryptedDatabase(SSEEncryptedDatabase):
    __slots__ = ["D"]  # dict D

    def __init__(self, D: dict, config: PiBasConfig = None):
        super(PiBasEncryptedDatabase, self).__init__(config)
        self.D = D

    @classmethod
    def build_from_list(cls, kv_pairs: list, config: PiBasConfig = None):
        kv_pairs.sort(key=lambda pair: pair[0])
        D = {key: value for key, value in kv_pairs}
        return cls(D, config)

    def serialize(self) -> bytes:
        data = PI_BAS_HEADER + pickle.dumps(self.D)
        return data

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiBasConfig = None):
        if xbytes[:len(PI_BAS_HEADER)] != PI_BAS_HEADER:
            raise ValueError("Parse header error.")

        data_bytes = xbytes[len(PI_BAS_HEADER):]
        D = pickle.loads(data_bytes)
        return cls(D)


class PiBasToken(SSEToken):
    __slots__ = ["K1", "K2"]  # K1, K2

    def __init__(self, K1: bytes, K2: bytes, config: PiBasConfig = None):
        super(PiBasToken, self).__init__(config)
        self.K1 = K1
        self.K2 = K2

    def serialize(self) -> bytes:
        return self.K1 + self.K2

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiBasConfig = None):
        if len(xbytes) != 2 * config.param_k:
            raise ValueError("The length of xbytes must be 2 times the length of the parameter param_k.")

        K1, K2 = xbytes[:config.param_k], xbytes[config.param_k:]

        return cls(K1, K2, config)


class PiBasResult(SSEResult):
    __slots__ = ["result"]

    def __init__(self, result: list, config: PiBasConfig = None):
        super(PiBasResult, self).__init__(config)
        self.result = result

    def serialize(self) -> bytes:
        return pickle.dumps(self.result)

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiBasConfig = None):
        result = pickle.loads(xbytes)
        if not isinstance(result, list):
            return ValueError("The data contained in xbytes is not a list.")

        return cls(result, config)
