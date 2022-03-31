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

from schemes.ANSS16.Scheme3.config import PiConfig, PI_HEADER
from schemes.interface.structures import SSEKey, SSEEncryptedDatabase, SSEToken, SSEResult
from toolkit.bytes_utils import split_bytes_given_slice_len


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

    def __eq__(self, other):
        if not isinstance(other, PiKey):
            return False
        return self.K == other.K


class PiEncryptedDatabase(SSEEncryptedDatabase):
    __slots__ = ["HT_S", "HT_L_list"]  # dict D

    def __init__(self, HT_S: dict, HT_list: list, config: PiConfig = None):
        super(PiEncryptedDatabase, self).__init__(config)
        self.HT_S = HT_S
        self.HT_L_list = HT_list

    @classmethod
    def create_hash_table(cls, kv_pairs: list):
        kv_pairs.sort(key=lambda pair: pair[0])
        D = {key: value for key, value in kv_pairs}
        return D

    def serialize(self) -> bytes:
        data = PI_HEADER + pickle.dumps((self.HT_S, self.HT_L_list))
        return data

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiConfig = None):
        if xbytes[:len(PI_HEADER)] != PI_HEADER:
            raise ValueError("Parse header error.")

        data_bytes = xbytes[len(PI_HEADER):]
        HT_S, HT_list = pickle.loads(data_bytes)
        return cls(HT_S, HT_list, config)

    def __eq__(self, other):
        if not isinstance(other, PiEncryptedDatabase):
            return False
        return self.HT_S == other.HT_S and self.HT_L_list == other.HT_L_list


class PiToken(SSEToken):
    __slots__ = ["li", "Ki", "li_prime", "Ki_prime"]  # τ

    def __init__(self, li: bytes, Ki: bytes, li_prime: bytes, Ki_prime: bytes, config: PiConfig = None):
        super(PiToken, self).__init__(config)
        self.li = li
        self.Ki = Ki
        self.li_prime = li_prime
        self.Ki_prime = Ki_prime

    def serialize(self) -> bytes:
        return self.li + self.Ki + self.li_prime + self.Ki_prime

    @classmethod
    def deserialize(cls, xbytes: bytes, config: PiConfig = None):
        if len(xbytes) != config.param_k + config.param_k_prime + config.param_l + config.param_l_prime:
            raise ValueError("The length of xbytes must be matched with config.")

        li, Ki, li_prime, Ki_prime = split_bytes_given_slice_len(xbytes, [config.param_l,
                                                                          config.param_k,
                                                                          config.param_l_prime,
                                                                          config.param_k_prime])

        return cls(li, Ki, li_prime, Ki_prime, config)

    def __eq__(self, other):
        if not isinstance(other, PiToken):
            return False
        return self.li == other.li \
               and self.Ki == other.Ki \
               and self.li_prime == other.li_prime \
               and self.Ki_prime == other.Ki_prime


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

    def __eq__(self, other):
        if not isinstance(other, PiResult):
            return False
        return self.result == other.result

    def get_result_list(self) -> list:
        return self.result
