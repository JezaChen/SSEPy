# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: hmac_luby_rackoff_prp.py 
@time: 2022/03/10
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""

from toolkit.prf.hmac_prf import HmacPRF
from toolkit.prp.abstraction import AbstractPRP
from toolkit.prp.luby_rackoff_prp import LubyRackoffPRP


class HmacLubyRackoffPRP(AbstractPRP):
    """Luby-Rackoff Construction where its underlying prp is HMAC-PRP"""

    def __init__(self, *, message_length: int, key_length: int, hash_func_name: "str" = "sha1"):
        super(HmacLubyRackoffPRP, self).__init__(message_length=message_length, key_length=key_length)
        if message_length % 2:
            raise ValueError("The message length needs to be divisible by 2.")
        if key_length % 3:
            raise ValueError("The key length needs to be divisible by 3.")
        underlying_prf = HmacPRF(output_length=message_length // 2,
                                 message_length=message_length // 2,
                                 key_length=key_length // 3,
                                 hash_func_name=hash_func_name)

        self.underlying_prp = LubyRackoffPRP(message_length=message_length,
                                             key_length=key_length,
                                             underlying_prf=underlying_prf)

    def __call__(self, key: bytes, message: bytes) -> bytes:
        return self.underlying_prp.__call__(key, message)
