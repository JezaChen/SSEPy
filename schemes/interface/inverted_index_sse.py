# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: inverted_index_sse.py 
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: Inverted Index Based SSE Scheme Abstraction
"""

import abc

from schemes.interface.structures import SSEKey, SSEToken, SSEEncryptedDatabase, SSEResult


# todo 有些SSE方案是可以允许所有方法是静态的, 而有些则应该分成客户端和服务端两个一起控制
class InvertedIndexSSE(metaclass=abc.ABCMeta):
    """Inverted Index Based SSE Scheme Abstraction, Based on [CGKO06]"""

    def __init__(self, *args, **kwargs):
        pass

    # def _parse_param_dict(self, param_dict: dict):
    #     for member in self.__slots__:
    #         if param_dict.get(member, None) is None:
    #             raise ValueError("param {} not exists.".format(member))
    #         setattr(self, member, param_dict[member])

    @abc.abstractmethod
    def KeyGen(self) -> SSEKey:
        pass

    @abc.abstractmethod
    def EDBSetup(self,
                 key: SSEKey,
                 database) -> SSEEncryptedDatabase:  # todo database abstraction
        pass

    @abc.abstractmethod
    def TokenGen(self,
                 key: SSEKey,
                 keyword: bytes) -> SSEToken:  # todo keyword abstraction, now is single-keyword
        pass

    @abc.abstractmethod
    def Search(self,
               edb: SSEEncryptedDatabase,
               token: SSEToken) -> SSEResult:
        pass
