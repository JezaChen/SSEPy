# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: structures.py 
@time: 2022/03/25
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import pickle
import typing

from schemes.DP17.Pi.config import PiConfig, PI_HEADER
from schemes.interface.structures import SSEKey, SSEEncryptedDatabase, SSEToken, SSEResult
from toolkit.bytes_utils import split_bytes_given_slice_len


class PiKey(SSEKey):
    __slots__ = ["k1", "k2", "k3"]

    def __init__(self,
                 k1: bytes,
                 k2: bytes,
                 k3: bytes,
                 config: PiConfig = None):
        super(PiKey, self).__init__(config)
        self.k1, self.k2, self.k3 = k1, k2, k3

    def serialize(self) -> bytes:
        return self.k1 + self.k2 + self.k3

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiConfig):
        if len(xbytes) != 3 * config.param_lambda:
            raise ValueError(
                "The length of xbytes must be three times the length of the parameter param_lambda."
            )
        k1, k2, k3 = split_bytes_given_slice_len(xbytes,
                                                 [config.param_lambda] * 3)

        return cls(k1, k2, k3, config)

    def __eq__(self, other):
        if not isinstance(other, PiKey):
            return False
        return self.k1 == other.k1 and self.k2 == other.k2 and self.k3 == other.k3


class PiEncryptedDatabase(SSEEncryptedDatabase):
    __slots__ = ["HT", "A_dict"]

    def __init__(self,
                 HT: dict,
                 A_dict: typing.Dict[int, typing.List[bytes]],
                 config: PiConfig = None):
        super(PiEncryptedDatabase, self).__init__(config)
        self.HT = HT
        self.A_dict = A_dict

    def serialize(self) -> bytes:
        data = PI_HEADER + pickle.dumps((self.HT, self.A_dict))
        return data

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiConfig = None):
        if xbytes[:len(PI_HEADER)] != PI_HEADER:
            raise ValueError("Parse header error.")

        HT, A_dict = pickle.loads(xbytes[len(PI_HEADER):])
        return cls(HT, A_dict, config=config)

    def __eq__(self, other):
        if not isinstance(other, PiEncryptedDatabase):
            return False
        return self.HT == other.HT and self.A_dict == other.A_dict


class PiToken(SSEToken):
    __slots__ = ["tag", "vtag", "etag"]

    def __init__(self,
                 tag: bytes,
                 vtag: bytes,
                 etag: bytes,
                 config: PiConfig = None):
        super(PiToken, self).__init__(config)
        self.tag, self.vtag, self.etag = tag, vtag, etag

    def serialize(self) -> bytes:
        return pickle.dumps((self.tag, self.vtag, self.etag))

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiConfig = None):
        tag, vtag, etag = pickle.loads(xbytes)

        return cls(tag, vtag, etag, config)

    def __eq__(self, other):
        if not isinstance(other, PiToken):
            return False
        return self.tag == other.tag and self.vtag == other.vtag and self.etag == other.etag


class PiResult(SSEResult):
    __slots__ = ["result"]

    def __init__(self, result: set, config: PiConfig = None):
        super(PiResult, self).__init__(config)
        self.result = result

    def serialize(self) -> bytes:
        return pickle.dumps(self.result)

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiConfig = None):
        result = pickle.loads(xbytes)
        if not isinstance(result, set):
            return ValueError("The data contained in xbytes is not a list.")

        return cls(result, config)

    def __str__(self):
        return self.result.__str__()

    def __eq__(self, other):
        if not isinstance(other, PiResult):
            return False
        return self.result == other.result

    def get_result_list(self) -> set:
        return self.result
