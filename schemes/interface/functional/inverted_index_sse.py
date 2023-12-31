# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: inverted_index_sse.py 
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: Inverted Index Based SSE Scheme Abstraction
"""

import abc
import typing

from schemes.interface.functional.function_marker import FuncTypes
from schemes.interface.structures import SSEKey, SSEToken, SSEEncryptedDatabase, SSEResult


def _dummy_constructor(config):
    raise NotImplementedError("This is a dummy function, you should not call it.")


class _DummyConfigCls:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("This is a dummy class, you should not instantiate it.")


# todo 有些SSE方案是可以允许所有方法是静态的, 而有些则应该分成客户端和服务端两个一起控制
class InvertedIndexSSE(metaclass=abc.ABCMeta):
    """Inverted Index Based SSE Scheme Abstraction, Based on [CGKO06]"""
    _constructor = _dummy_constructor
    _default_config = {}
    _config_class = _DummyConfigCls

    def __init__(self, config: typing.Optional[dict] = None):
        if config is None:
            config = self._default_config
        self.config = type(self)._config_class(config)
        functions = type(self)._constructor(self.config)
        self._parse_exported_functions(functions)

    def _parse_exported_functions(self, exported_functions: tuple):
        for func in exported_functions:
            if func.__sse_private_func_type__ == FuncTypes.KeyGen:
                self.KeyGen = func
            elif func.__sse_private_func_type__ == FuncTypes.EDBSetup:
                self.EDBSetup = func
            elif func.__sse_private_func_type__ == FuncTypes.TokenGen:
                self.TokenGen = func
            elif func.__sse_private_func_type__ == FuncTypes.Search:
                self.Search = func
            else:
                raise ValueError("Unknown function type.")

    def KeyGen(self) -> SSEKey:
        raise NotImplementedError

    def EDBSetup(self,
                 key: SSEKey,
                 database) -> SSEEncryptedDatabase:  # todo database abstraction
        raise NotImplementedError

    def TokenGen(self,
                 key: SSEKey,
                 keyword: bytes) -> SSEToken:  # todo keyword abstraction, now is single-keyword
        raise NotImplementedError

    def Search(self,
               edb: SSEEncryptedDatabase,
               token: SSEToken) -> SSEResult:
        raise NotImplementedError
