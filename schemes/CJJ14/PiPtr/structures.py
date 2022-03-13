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

from schemes.CJJ14.PiPtr.config import PiPtrConfig, PI_PTR_HEADER
from schemes.interface.structures import SSEKey, SSEEncryptedDatabase, SSEToken, SSEResult


class PiPtrKey(SSEKey):
    __slots__ = ["K"]

    def __init__(self, K: bytes, config: PiPtrConfig = None):
        super(PiPtrKey, self).__init__(config)
        self.K = K

    def serialize(self) -> bytes:
        return self.K

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiPtrConfig):
        if len(xbytes) != config.param_lambda:
            raise ValueError("The length of xbytes must be the same as the length of the parameter param_k.")

        return cls(xbytes)


class PiPtrEncryptedDatabase(SSEEncryptedDatabase):
    __slots__ = ["D", "A"]  # dict D, array A

    def __init__(self, D: dict, A: list, config: PiPtrConfig = None):
        super(PiPtrEncryptedDatabase, self).__init__(config)
        self.D = D
        self.A = A

    @staticmethod
    def create_dictionary_from_list(kv_pairs: list) -> dict:
        kv_pairs.sort(key=lambda pair: pair[0])
        D = {key: value for key, value in kv_pairs}
        return D

    def serialize(self) -> bytes:
        data = PI_PTR_HEADER + pickle.dumps((self.D, self.A))
        return data

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiPtrConfig = None):
        if xbytes[:len(PI_PTR_HEADER)] != PI_PTR_HEADER:
            raise ValueError("Parse header error.")

        data_bytes = xbytes[len(PI_PTR_HEADER):]
        D, A = pickle.loads(data_bytes)
        return cls(D, A)


class PiPtrToken(SSEToken):
    __slots__ = ["K1", "K2"]  # K1, K2

    def __init__(self, K1: bytes, K2: bytes, config: PiPtrConfig = None):
        super(PiPtrToken, self).__init__(config)
        self.K1 = K1
        self.K2 = K2

    def serialize(self) -> bytes:
        return self.K1 + self.K2

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiPtrConfig = None):
        if len(xbytes) != 2 * config.param_k:
            raise ValueError("The length of xbytes must be 2 times the length of the parameter param_k.")

        K1, K2 = xbytes[:config.param_k], xbytes[config.param_k:]

        return cls(K1, K2, config)


class PiPtrResult(SSEResult):
    __slots__ = ["result"]

    def __init__(self, result: list, config: PiPtrConfig = None):
        super(PiPtrResult, self).__init__(config)
        self.result = result

    def serialize(self) -> bytes:
        return pickle.dumps(self.result)

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiPtrConfig = None):
        result = pickle.loads(xbytes)
        if not isinstance(result, list):
            return ValueError("The data contained in xbytes is not a list.")

        return cls(result, config)
