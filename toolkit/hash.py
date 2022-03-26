# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: hash.py 
@time: 2022/03/25
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import abc
import functools
import hashlib

from toolkit.bytes_utils import int_to_bytes
from toolkit.constants import LENGTH_NOT_GIVEN


class AbstractHash(metaclass=abc.ABCMeta):
    def __init__(self, *, output_length: int):
        self.output_length = output_length

    def __call__(self, message: bytes) -> bytes:
        raise NotImplementedError("Class AbstractHash is an abstract class.")


class HashlibHashVariableOutputLengthWrapper(AbstractHash):
    """Wrap hash functions of hashlib to support variable length output
    """

    def __init__(self, *, output_length: int = LENGTH_NOT_GIVEN, hash_func_name: str):
        super(HashlibHashVariableOutputLengthWrapper, self).__init__(output_length=output_length)
        if hash_func_name not in hashlib.algorithms_available:
            raise ValueError("Hash type {} is not supported".format(hash_func_name))

        hash_func = functools.partial(hashlib.new, hash_func_name)
        if output_length == LENGTH_NOT_GIVEN:
            self.output_length = hash_func(b"").digest_size

        self.hash_func_name = hash_func_name
        self.hash_func = hash_func

    def _ctr_expand(self, message: bytes):
        """Extended output length using counter mode"""
        result = b''
        c = 1
        while len(result) < self.output_length:
            result += self.hash_func(message + int_to_bytes(c)).digest()
            c += 1
        return result[:self.output_length]

    def __call__(self, message: bytes) -> bytes:
        if self.hash_func_name in {"shake_128", "shake_256"}:
            return self.hash_func(message).digest(self.output_length)
        return self._ctr_expand(message)


__builtin_hash_functions_cache = {}


def get_hash_implementation(hash_function_name: str):
    cache = __builtin_hash_functions_cache
    hash_function = cache.get(hash_function_name)
    if hash_function is not None:
        return hash_function

    if hash_function_name in hashlib.algorithms_available:
        cache[hash_function_name] = functools.partial(HashlibHashVariableOutputLengthWrapper,
                                                      hash_func_name=hash_function_name)

    hash_function = cache.get(hash_function_name)
    if hash_function is not None:
        return hash_function

    raise ValueError('unsupported Hash type ' + hash_function_name)
