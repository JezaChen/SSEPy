# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: prp.py 
@time: 2022/03/09
@contact: jeza@vip.qq.com
@software: PyCharm 
@description: Pseudorandom Permutation Implementation
@chinese_description: 伪随机置换实现
"""
import abc

import toolkit.prf
from toolkit.bytes_utils import bytes_xor
from toolkit.prf import AbstractPRF


class AbstractPRP(metaclass=abc.ABCMeta):
    def __init__(self, *, message_length: int, key_length: int):
        self.key_length = key_length
        self.message_length = message_length

    def __call__(self, key: bytes, message: bytes) -> bytes:
        raise NotImplementedError("Class AbstractPRP is an abstract class.")


class LubyRackoffPRP(AbstractPRP):
    """
    Luby-Rackoff Construction. To construct a PRP from a PRF
    @note: Instead of inheriting directly from the RubyRackoffPRP class, it is used here as a member
    """

    def __init__(self, *, message_length: int, key_length: int, underlying_prf: AbstractPRF):
        super(LubyRackoffPRP, self).__init__(message_length=message_length, key_length=key_length)
        if underlying_prf.key_length * 3 != key_length:
            raise ValueError("The key length of the PRP needs to be 3 times the length of the underlying PRF key.")
        if underlying_prf.message_length != underlying_prf.output_length:
            raise ValueError("The input length of the PRF needs to be equal to the output length.")
        if underlying_prf.message_length * 2 != message_length:
            # This implies that the message length of this PRP needs to be an even number
            raise ValueError(
                "The input (output) length of the PRP needs to be equal to twice the input length of the PRF."
            )

        self.underlying_prf = underlying_prf

    def __call__(self, key: bytes, message: bytes) -> bytes:
        if len(key) != self.key_length:
            raise ValueError("Key length mismatch for PRP.")
        if len(message) != self.message_length:
            raise ValueError("Message(Input) length mismatch for PRP.")

        curr_left, curr_right = message[:self.message_length // 2], message[self.message_length // 2:]
        # K0, K1, K2
        key_list = [key[i: i + self.key_length // 3] for i in range(0, self.key_length, self.key_length // 3)]

        for i in range(3):
            next_left, next_right = curr_right, bytes_xor(curr_left, self.underlying_prf(key_list[i], curr_right))
            curr_left, curr_right = next_left, next_right

        return curr_left + curr_right


class HmacLubyRackoffPRP(AbstractPRP):
    """Luby-Rackoff Construction where its underlying prp is HMAC-PRP"""

    def __init__(self, *, message_length: int, key_length: int, hash_func_name: "str" = "sha1"):
        super(HmacLubyRackoffPRP, self).__init__(message_length=message_length, key_length=key_length)
        if message_length % 2:
            raise ValueError("The message length needs to be divisible by 2.")
        if key_length % 3:
            raise ValueError("The key length needs to be divisible by 3.")
        underlying_prf = toolkit.prf.HmacPRF(output_length=message_length // 2,
                                             message_length=message_length // 2,
                                             key_length=key_length // 3,
                                             hash_func_name=hash_func_name)

        self.underlying_prp = LubyRackoffPRP(message_length=message_length,
                                             key_length=key_length,
                                             underlying_prf=underlying_prf)

    def __call__(self, key: bytes, message: bytes) -> bytes:
        return self.underlying_prp.__call__(key, message)
