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


class PersistentBytesDict(metaclass=ABCMeta):
    """ Persistent Bytes Dictionary,
    where the type of keys and values is `byte`.
    """

    @classmethod
    @abstractmethod
    def open(cls, dict_path: str, create_only: bool = False) -> 'PersistentBytesDict':
        """
        Open a persistent dictionary based on the local path
        :param dict_path: The local path of dictionary storage,
        according to which a persistent dictionary can be instantiated.
        :param create_only: Whether only a new persistent dictionary can be created,
        in other words, the path cannot correspond to an existing persistent dictionary.
        """

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
    def __contains__(self, key: bytes): ...

    @abstractmethod
    def __getitem__(self, key: bytes): ...

    @abstractmethod
    def __setitem__(self, key: bytes, value: bytes): ...

    @abstractmethod
    def __delitem__(self, key: bytes): ...

    @abstractmethod
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    def __del__(self): ...

    @abstractmethod
    def clear(self): ...

    @property
    @abstractmethod
    def dict_local_path(self): ...

    @classmethod
    @abstractmethod
    def from_dict(cls, dict_: dict, dict_path: str) -> 'PersistentBytesDict': ...
