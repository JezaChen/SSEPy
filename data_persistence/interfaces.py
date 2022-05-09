# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: interfaces.py
@time: 2022/05/08
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import typing
from abc import ABCMeta, abstractmethod


class PersistentDict(metaclass=ABCMeta):
    """ Persistent Dictionary Static Protocol
    """

    @classmethod
    @abstractmethod
    def open(cls, file_path: str) -> 'PersistentDict': ...

    @abstractmethod
    def sync(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def __iter__(self): ...

    @abstractmethod
    def __len__(self): ...

    @abstractmethod
    def get(self, key, default=None): ...

    @abstractmethod
    def __contains__(self, item): ...

    @abstractmethod
    def __getitem__(self, item): ...

    @abstractmethod
    def __setitem__(self, key, value): ...

    @abstractmethod
    def __delitem__(self, key): ...

    @abstractmethod
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    def __del__(self): ...
