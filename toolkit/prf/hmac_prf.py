# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: hmac_prf.py 
@time: 2022/03/10
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""

import functools
import hashlib
import hmac

from toolkit.constants import LENGTH_UNLIMITED, LENGTH_NOT_GIVEN
from toolkit.prf.abstraction import AbstractPRF


def _tls_p_hash(key: bytes,
                message: bytes,
                output_len: int,
                hash_func_name: "str" = "sha1") -> bytes:
    """
    A data expansion function defined in section 5 of RFC 4346 (or section 5 of RFC 5246)
    In RFC 4346 (or RFC 5246), P_hash(secret, data) uses a single hash function to expand
    a secret and seed into an arbitrary quantity of output:
    :param key: the key of HMAC, the secret parameter of P_hash function
    :param message: the input message of HMAC, the data parameter of P_hash function
    :param output_len: the output length
    :return: bytes, the tag of the message
    """
    if hash_func_name not in hashlib.algorithms_available:
        raise ValueError(
            "Hash type {} is not supported".format(hash_func_name))

    hash_func = functools.partial(hmac.new, digestmod=hash_func_name)

    hash_len = hash_func(key, b"").digest_size
    n = (output_len + hash_len - 1) // hash_len

    res = b""
    a = hash_func(key, message).digest()  # A(1)

    while n > 0:
        res += hash_func(key, a + message).digest()
        a = hash_func(key, a).digest()
        n -= 1

    return res[:output_len]


class HmacPRF(AbstractPRF):
    """The HMAC function being used as a PRF, described in NIST SP 800-35 Rev. 1."""

    def __init__(self,
                 *,
                 output_length: int = LENGTH_NOT_GIVEN,
                 key_length: int = LENGTH_UNLIMITED,
                 message_length: int = LENGTH_UNLIMITED,
                 hash_func_name: str = "sha1"):
        """
        Constructor of HMAC-PRF
        :param output_length: The length of output values
        :param key_length: The length of keys, LENGTH_UNLIMITED represents no limit
        :param message_length: The length of message, LENGTH_UNLIMITED represents no limit
        """
        super(HmacPRF, self).__init__(output_length=output_length,
                                      message_length=message_length,
                                      key_length=key_length)
        if hash_func_name not in hashlib.algorithms_available:
            raise ValueError(
                "Hash type {} is not supported".format(hash_func_name))
        self.hash_func_name = hash_func_name
        if output_length == LENGTH_NOT_GIVEN:
            self.output_length = hmac.new(
                b"", b"", digestmod=self.hash_func_name).digest_size

    def __call__(self, key: bytes, message: bytes) -> bytes:
        if self.key_length != LENGTH_UNLIMITED and len(key) != self.key_length:
            raise ValueError(
                "The key length of the PRF does not meet the definition.")
        if self.message_length != LENGTH_UNLIMITED and len(
                message) != self.message_length:
            raise ValueError(
                "The message length of the PRF does not meet the definition")

        return _tls_p_hash(key, message, self.output_length,
                           self.hash_func_name)
