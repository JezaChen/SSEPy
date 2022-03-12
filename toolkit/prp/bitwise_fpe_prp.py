# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: bitwise_fpe_prp.py 
@time: 2022/03/12
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
from toolkit.bits import Bitset
from toolkit.prp.abstraction import AbstractBitwisePRP
from toolkit.symmetric_encryption.fpe import BitwiseFFX


class BitwiseFPEPRP(AbstractBitwisePRP):
    """Luby-Rackoff Construction where its underlying prp is HMAC-PRP"""

    def __init__(self, *, message_bit_length: int, key_bit_length: int):
        super(BitwiseFPEPRP, self).__init__(message_bit_length=message_bit_length,
                                                 key_bit_length=key_bit_length)
        self.underlying_fpe = BitwiseFFX()

    def __call__(self, key: Bitset, message: Bitset) -> Bitset:
        if len(key) != self.key_bit_length:
            raise ValueError("Key bit length mismatch for PRP.")
        if len(message) != self.message_bit_length:
            raise ValueError("Message(Input) bit length mismatch for PRP.")

        return self.underlying_fpe.encrypt(bytes(key), message)
