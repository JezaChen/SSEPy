# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: persistent_dict.py
@time: 2022/05/08
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import typing

from data_persistence.interfaces import PersistentDict
import shelve
import pickle


class PickledDict(PersistentDict):
    """ A naive persistent dictionary, based on dict and pickle lib
    """

    @classmethod
    def open(cls, file_path: str) -> 'PickledDict':
        return cls(file_path)

    def __init__(self, file_path: str):
        self.__data = {}
        self.__file = None
        with open(file_path) as self.__file:
            self.__data = pickle.load(self.__file)
            if not isinstance(self.__data, typing.Dict):
                raise TypeError(f"The data of argument file_path {file_path} is not an instance of dict")

    def sync(self) -> None:
        pickle.dumps()

    def close(self) -> None:
        self.__shelf.close()

    def __iter__(self):
        return iter(self.__shelf)

    def __len__(self):
        return len(self.__shelf)

    def get(self, key, default=None):
        return self.__shelf.get(key, default=default)

    def __contains__(self, item):
        return item in self.__shelf

    def __getitem__(self, item):
        return self.__shelf[item]

    def __setitem__(self, key, value):
        self.__shelf[key] = value

    def __delitem__(self, key):
        del self.__shelf[key]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()


class DBMDict(PersistentDict):
    """ A simple persistent dictionary, based on shelve.Shelf
    """

    @classmethod
    def open(cls, file_path: str) -> 'DBMDict':
        return cls(file_path)

    def __init__(self, file_path: str):
        self.__shelf = shelve.open(file_path, writeback=True)

    def sync(self) -> None:
        self.__shelf.sync()

    def close(self) -> None:
        self.__shelf.close()

    def __iter__(self):
        return iter(self.__shelf)

    def __len__(self):
        return len(self.__shelf)

    def get(self, key, default=None):
        return self.__shelf.get(key, default=default)

    def __contains__(self, item):
        return item in self.__shelf

    def __getitem__(self, item):
        return self.__shelf[item]

    def __setitem__(self, key, value):
        self.__shelf[key] = value

    def __delitem__(self, key):
        del self.__shelf[key]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    d = DBMDict.open("test.db")
    print(d["ss"])
