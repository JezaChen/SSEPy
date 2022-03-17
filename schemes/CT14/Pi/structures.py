# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: structures.py 
@time: 2022/03/11
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import pickle

from schemes.CT14.Pi.config import PiConfig, PI_HEADER
from schemes.interface.structures import SSEKey, SSEEncryptedDatabase, SSEToken, SSEResult


class PiKey(SSEKey):
    __slots__ = ["K"]

    def __init__(self, K: bytes, config: PiConfig = None):
        super(PiKey, self).__init__(config)
        self.K = K

    def serialize(self) -> bytes:
        return self.K

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiConfig):
        if len(xbytes) != config.param_k:
            raise ValueError("The length of xbytes must be the same as the length of the parameter param_lambda.")

        return cls(xbytes)


class PiEncryptedDatabase(SSEEncryptedDatabase):
    __slots__ = ["HT_list"]  # dict D

    def __init__(self, HT_list: list, config: PiConfig = None):
        super(PiEncryptedDatabase, self).__init__(config)
        self.HT_list = HT_list

    @classmethod
    def create_hash_table(cls, kv_pairs: list):
        kv_pairs.sort(key=lambda pair: pair[0])
        D = {key: value for key, value in kv_pairs}
        return D

    def serialize(self) -> bytes:
        data = PI_HEADER + pickle.dumps(self.HT_list)
        return data

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiConfig = None):
        if xbytes[:len(PI_HEADER)] != PI_HEADER:
            raise ValueError("Parse header error.")

        data_bytes = xbytes[len(PI_HEADER):]
        HT_list = pickle.loads(data_bytes)
        return cls(HT_list, config)


class PiToken(SSEToken):
    __slots__ = ["K0", "K1"]  # K_{w,0}, K_{w,1}

    def __init__(self, K0: bytes, K1: bytes, config: PiConfig = None):
        super(PiToken, self).__init__(config)
        self.K0 = K0
        self.K1 = K1

    def serialize(self) -> bytes:
        return self.K0 + self.K1

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiConfig = None):
        if len(xbytes) != config.param_k + config.param_k_prime:
            raise ValueError("The length of xbytes must be param_k + param_k_prime.")

        K1, K2 = xbytes[:config.param_k], xbytes[config.param_k:]

        return cls(K1, K2, config)


class PiResult(SSEResult):
    __slots__ = ["result"]

    def __init__(self, result: list, config: PiConfig = None):
        super(PiResult, self).__init__(config)
        self.result = result

    def serialize(self) -> bytes:
        return pickle.dumps(self.result)

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiConfig = None):
        result = pickle.loads(xbytes)
        if not isinstance(result, list):
            return ValueError("The data contained in xbytes is not a list.")

        return cls(result, config)

    def __str__(self):
        return self.result.__str__()
