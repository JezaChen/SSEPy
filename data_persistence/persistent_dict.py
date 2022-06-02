# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: persistent_array.py
@time: 2022/05/08
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import collections.abc
import os.path
import threading
import typing

from data_persistence.interfaces import PersistentBytesDict
import data_persistence.bytes_shelf
import pickle

__all__ = ["PickledDict", "DBMDict"]


class _ClosedDict(collections.abc.MutableMapping):
    """Marker for a closed dict.  Access attempts raise a ValueError."""

    def closed(self, *args):
        raise ValueError('invalid operation on closed dict')

    __iter__ = __len__ = __getitem__ = __setitem__ = __delitem__ = keys = closed

    def __repr__(self):
        return '<Closed Dictionary>'


class PickledDict(PersistentBytesDict):
    """ A naive persistent dictionary, based on dict and pickle lib
    """

    @classmethod
    def open(cls, file_path: str, create_only: bool = False) -> 'PickledDict':
        return cls(file_path, create_only)

    def __init__(self, file_path: str, create_only: bool = False):
        self.__file_path = file_path
        self.__data = {}
        try:
            self.__file = open(file_path, "rb+")
            if create_only:
                raise FileExistsError(f"The file {file_path} exists, and you set the parameter create_only to True.")

            self.__data = pickle.load(self.__file)

            if not isinstance(self.__data, typing.Dict):
                raise TypeError(f"The data of argument file_path {file_path} is not an instance of dict")
        except FileNotFoundError:  # create a new file for pickling
            self.__file = open(file_path, "wb+")
        except (TypeError, pickle.UnpicklingError):
            self.__file.close()
            raise

    def sync(self) -> None:
        self.__file.truncate(0)
        self.__file.seek(0)
        pickle.dump(self.__data, self.__file)
        self.__file.flush()

    def close(self) -> None:
        try:
            if not self.__file.closed:
                self.sync()
                self.__file.close()
        finally:
            try:
                self.__data = _ClosedDict()
            except:
                self.__data = None

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def get(self, key: bytes, default=None):
        return self.__data.get(key, default=default)

    def __contains__(self, key: bytes):
        return key in self.__data

    def __getitem__(self, key: bytes):
        return self.__data[key]

    def __setitem__(self, key: bytes, value: bytes):
        self.__data[key] = value

    def __delitem__(self, key: bytes):
        del self.__data[key]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def clear(self):
        self.__data = {}

    @property
    def dict_local_path(self):
        return self.__file_path

    @classmethod
    def from_dict(cls, dict_: dict, dict_path: str) -> 'PickledDict':
        pickled_dict = cls(dict_path, create_only=True)
        pickled_dict.__data = dict(dict_)  # Be Careful, Copy!
        pickled_dict.sync()
        return pickled_dict


class DBMDict(PersistentBytesDict):
    """ A simple persistent dictionary, based on shelve.BytesShelf
    """

    """ Threading Lock
    Dbm does not allow concurrent opening of database files.
    """
    __thread_lock_map = collections.defaultdict(lambda: threading.Lock())

    @classmethod
    def open(cls, file_path: str, create_only: bool = False) -> 'DBMDict':
        return cls(file_path, create_only)

    def __init__(self, file_path: str, create_only: bool = False):
        self.__thread_lock_map[file_path].acquire()

        if create_only and os.path.exists(file_path):
            raise FileExistsError(f"The file {file_path} exists, and you set the parameter create_only to True.")

        self.__file_path = file_path
        self.__shelf = data_persistence.bytes_shelf.open(file_path, writeback=True)
        self.__closed = False

    def sync(self) -> None:
        self.__shelf.sync()

    def close(self) -> None:
        if self.__closed:  # Already Closed
            return

        try:
            self.__shelf.close()
            self.__shelf = _ClosedDict()
            self.__closed = True
        finally:
            self.__thread_lock_map[self.__file_path].release()

    def __iter__(self):
        return iter(self.__shelf)

    def __len__(self):
        return len(self.__shelf)

    def get(self, key: bytes, default=None):
        return self.__shelf.get(key, default=default)

    def __contains__(self, key: bytes):
        return key in self.__shelf

    def __getitem__(self, key: bytes):
        return self.__shelf[key]

    def __setitem__(self, key: bytes, value):
        self.__shelf[key] = value

    def __delitem__(self, key: bytes):
        del self.__shelf[key]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def clear(self):
        self.__shelf.clear()

    @property
    def dict_local_path(self):
        return self.__file_path

    @classmethod
    def from_dict(cls, dict_: dict, dict_path: str) -> 'DBMDict':
        pickled_dict = cls(dict_path, create_only=True)
        pickled_dict.__shelf.update(dict_)
        pickled_dict.sync()
        return pickled_dict
