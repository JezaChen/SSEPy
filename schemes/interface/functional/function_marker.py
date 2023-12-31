# -*- coding:utf-8 _*-
"""
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: function_marker.py
@time: 2023/12/31
@contact: jeza@vip.qq.com
@site:
@software: PyCharm
@description: SSE Function Marker
"""


class FuncTypes:
    KeyGen = 0
    EDBSetup = 1
    TokenGen = 2
    Search = 3


class SSEFunctions:
    @staticmethod
    def KeyGen(func):
        func.__sse_private_func_type__ = FuncTypes.KeyGen
        return func

    @staticmethod
    def EDBSetup(func):
        func.__sse_private_func_type__ = FuncTypes.EDBSetup
        return func

    @staticmethod
    def TokenGen(func):
        func.__sse_private_func_type__ = FuncTypes.TokenGen
        return func

    @staticmethod
    def Search(func):
        func.__sse_private_func_type__ = FuncTypes.Search
        return func
