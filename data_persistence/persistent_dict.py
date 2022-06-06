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
    def open(cls, local_path: str, create_only: bool = False) -> 'PickledDict':
        return cls(local_path, "r")

    @classmethod
    def create(cls, local_path: str, **_) -> 'PickledDict':
        return cls(local_path, "c")

    def __init__(self, file_path: str, mode: str = "r"):
        self.__file_path = file_path
        self.__data = {}
        self.__file = None
        if mode == "r":  # read
            try:
                self.__file = open(file_path, "rb+")
                self.__data = pickle.load(self.__file)
                if not isinstance(self.__data, typing.Dict):
                    raise TypeError(f"The data of argument file_path {file_path} is not an instance of dict")
            except FileNotFoundError:
                raise FileNotFoundError(f"The dict corresponding to the local path {file_path} not exists.")
            except (TypeError, pickle.UnpicklingError):
                self.__file.close()
                raise

        elif mode == "c":  # create
            if os.path.exists(file_path):
                raise FileExistsError(f"The file {file_path} exists.")
            self.__file = open(file_path, "wb+")

        else:  # Unexpected mode
            raise TypeError(f"Unexpected Mode: {mode}")

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
        except AttributeError:  # self.__file may be None
            pass
        finally:
            try:
                self.__data = _ClosedDict()
            except:
                self.__data = None

    def release(self) -> None:
        self.close()
        if os.path.exists(self.__file_path):  # may be released multiple times
            os.unlink(self.__file_path)

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def get(self, key: bytes, default=None):
        return self.__data.get(key, default)

    def __contains__(self, key: bytes):
        return key in self.__data

    def __getitem__(self, key: bytes):
        return self.__data[key]

    def __setitem__(self, key: bytes, value: bytes):
        # check if the value is a byte-string
        if not isinstance(value, typing.ByteString):
            raise TypeError(
                "The content should be a byte string."
            )

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
        pickled_dict = cls(dict_path, mode="c")
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
    def open(cls, local_path: str, create_only: bool = False) -> 'DBMDict':
        return cls(local_path, "r")

    @classmethod
    def create(cls, local_path: str, *, wait=False, **config) -> 'DBMDict':
        return cls(local_path, "c")

    def __init__(self, file_path: str, mode: str = "r"):
        self.__file_path = file_path
        self.__closed = False
        self.__shelf = None
        # check validity only
        if mode == "r":  # read
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The dict corresponding to the local path {file_path} not exists.")
        elif mode == "c":  # create
            if os.path.exists(file_path):
                raise FileExistsError(f"The file {file_path} exists.")
        else:  # unexpected mode
            raise TypeError(f"Unexpected Mode: {mode}")

        self.__thread_lock_map[file_path].acquire()
        self.__shelf = data_persistence.bytes_shelf.open(file_path, writeback=True)

    def sync(self) -> None:
        self.__shelf.sync()

    def close(self) -> None:
        if self.__closed:  # Already Closed
            return
        try:
            self.__shelf.close()
        except AttributeError:  # __shelf may be None, because it may be released when __init__ method is not completed
            pass
        finally:
            try:
                self.__closed = True
                self.__thread_lock_map[self.__file_path].release()
                self.__shelf = _ClosedDict()
            except RuntimeError as e:
                if len(e.args) != 1 or e.args[0] != "release unlocked lock":
                    raise
            except:
                self.__shelf = None

    def release(self) -> None:
        self.close()
        if os.path.exists(self.__file_path):  # may be released multiple times
            os.unlink(self.__file_path)

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
        # check if the value is a byte-string
        if not isinstance(value, typing.ByteString):
            raise TypeError(
                "The content should be a byte string."
            )

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
        pickled_dict = cls(dict_path, mode="c")
        pickled_dict.__shelf.update(dict_)
        pickled_dict.sync()
        return pickled_dict
