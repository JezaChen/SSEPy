# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: structures.py 
@time: 2022/03/10
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import pickle

from schemes.CGKO06.SSE1.param import param_k, SSE1_HEADER, prp_pi, prf_f
from schemes.interface.structures import SSEKey, SSEEncryptedDatabase, SSEToken, SSEResult


class SSE1Key(SSEKey):
    __slots__ = ["K1", "K2", "K3", "K4"]

    def __init__(self, K1: bytes, K2: bytes, K3: bytes, K4: bytes):
        self.K1, self.K2, self.K3, self.K4 = K1, K2, K3, K4

    def serialize(self) -> bytes:
        return b''.join([self.K1, self.K2, self.K3, self.K4])

    @classmethod
    def deserialize(cls, xbytes: bytes):
        if len(xbytes) != 4 * param_k:
            raise ValueError("The length of xbytes must be four times the length of the parameter param_k.")

        key_list = [xbytes[i: i + param_k] for i in range(0, len(xbytes), param_k)]
        return cls(*key_list)


class SSE1EncryptedDatabase(SSEEncryptedDatabase):
    __slots__ = ["A", "T"]  # array A and look-up table T

    def __init__(self, A: list, T: dict):
        self.A, self.T = A, T

    def serialize(self) -> bytes:
        data = SSE1_HEADER + pickle.dumps((self.A, self.T))
        return data

    @classmethod
    def deserialize(cls, xbytes: bytes):
        if xbytes[:len(SSE1_HEADER)] != SSE1_HEADER:
            raise ValueError("Parse header error.")

        data_bytes = xbytes[len(SSE1_HEADER):]
        A, T = pickle.loads(data_bytes)
        return cls(A, T)


class SSE1Token(SSEToken):
    __slots__ = ["gamma", "eta"]  # array A and look-up table T

    def __init__(self, gamma: bytes, eta: bytes):
        self.gamma, self.eta = gamma, eta

    def serialize(self) -> bytes:
        return self.gamma + self.eta

    @classmethod
    def deserialize(cls, xbytes: bytes):
        if len(xbytes) != prp_pi.message_length + prf_f.output_length:
            raise ValueError("The length of xbytes is wrong.")

        gamma, eta = xbytes[:prp_pi.message_length], xbytes[prp_pi.message_length:]
        return cls(gamma, eta)


class SSE1Result(SSEResult):
    __slots__ = ["result"]  # array A and look-up table T

    def __init__(self, result: list):
        self.result = result

    def serialize(self) -> bytes:
        return pickle.dumps(self.result)

    @classmethod
    def deserialize(cls, xbytes: bytes):
        result = pickle.loads(xbytes)
        if not isinstance(result, list):
            return ValueError("The data contained in xbytes is not a list.")

        return cls(result)
