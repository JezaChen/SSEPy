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
import array
import collections.abc
import operator
import typing
from abc import ABCMeta, abstractmethod

__all__ = ["PersistentBytesDict", "PersistentFixedLengthBytesArray"]

from typing import overload, Iterable, MutableSequence


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
    def sync(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def __iter__(self):
        ...

    @abstractmethod
    def __len__(self):
        ...

    def get(self, key, default=None):
        for k in self:
            if k == key:
                return self[key]
        return default

    def __contains__(self, key: bytes):
        for k in self:
            if k == key:
                return True
        return False

    @abstractmethod
    def __getitem__(self, key: bytes):
        ...

    @abstractmethod
    def __setitem__(self, key: bytes, value: bytes):
        ...

    @abstractmethod
    def __delitem__(self, key: bytes):
        ...

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abstractmethod
    def __del__(self):
        ...

    def clear(self):
        for key in list(iter(self)):  # copy keys and delete
            del self[key]

    @property
    @abstractmethod
    def dict_local_path(self):
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, dict_: dict, dict_path: str) -> 'PersistentBytesDict':
        ...


class PersistentFixedLengthBytesArray(collections.abc.Sequence, metaclass=ABCMeta):
    """ Persistent Fixed-length Bytes Array,
    where the type of all items is `byte` and of fixed length,
    and the length of the array is fixed,
    which implies you CANNOT insert and delete items.

    """

    @classmethod
    @abstractmethod
    def open(cls,
             local_path: str) -> 'PersistentFixedLengthBytesArray':
        """
        Open a persistent array based on the local path
        :param local_path: The local path of list storage,
        according to which a persistent list can be instantiated.
        """

    @classmethod
    @abstractmethod
    def create(cls,
               local_path: str,
               **config) -> 'PersistentFixedLengthBytesArray':
        """ Given the element size and array length,
        create a blank byte array and save it to the file corresponding to local_path.
        If the file corresponding to local_path already exists, a FileExistsError exception is thrown
        :param local_path: The path to save the persistent byte array.
        Note that the concrete implementation does not necessarily save only
        on the single file represented by that path; in other words, local_path is just a token,
        and the concrete implementation may create multiple related files for saving based on it
        :param config for file creating
        item_size: the fixed size of bytes stored in the array
        array_len: the fixed length of the array to create
        """

    @abstractmethod
    def sync(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @overload
    @abstractmethod
    def __getitem__(self, i: int) -> bytes:
        ...

    @overload
    @abstractmethod
    def __getitem__(self, s: slice) -> MutableSequence[bytes]:
        ...

    def __getitem__(self, i) -> bytes:
        pass

    @overload
    @abstractmethod
    def __setitem__(self, i: int, o: bytes) -> None:
        ...

    @overload
    @abstractmethod
    def __setitem__(self, s: slice, o: Iterable[bytes]) -> None:
        ...

    def __setitem__(self, i, o) -> None:
        pass

    @overload
    @abstractmethod
    def __delitem__(self, i: int) -> None:
        ...

    @overload
    @abstractmethod
    def __delitem__(self, i: slice) -> None:
        ...

    def __delitem__(self, i) -> None:
        """ In fixed-length Bytes arrays, the __delitem__ method simply
        assigns the element at the specified position to all zeros,
        rather than actually deleting the element at that position.
        """
        if isinstance(i, slice):
            start, stop, stride = i.indices(len(self))
            for index in range(start, stop, stride):
                self._set_all_zeros_by_index(index)
            return

        # else...
        index = operator.index(i)
        self._set_all_zeros_by_index(index)

    def _set_all_zeros_by_index(self, index: int):
        """ Set the item corresponding to index to all zero bytes.
        """
        self[index] = b"\x00" * self.item_size

    @abstractmethod
    def __len__(self) -> int:
        pass

    def __iter__(self):
        for index in range(len(self)):
            yield self[index]

    def clear(self):
        """ The clear method for persistent fixed-length byte arrays does not delete the file,
        but simply sets all bytes to all zeros.
        """
        for i in range(len(self)):
            del self[i]

    @abstractmethod
    def release(self):
        """ The release method will delete the local file(s) of the array.
        """

    @property
    @abstractmethod
    def local_path(self):
        ...

    @property
    @abstractmethod
    def item_size(self):
        ...

    @classmethod
    @abstractmethod
    def from_list(cls,
                  list_: list[bytes],
                  local_path: str,
                  *config_args,
                  **config_kwargs) -> 'PersistentFixedLengthBytesArray':
        """
        :param list_: List of bytes
        :param local_path: The local path to store the persistent array
        :param config_args: Positional parameters for configuring the creation operation
        :param config_kwargs: Keyword parameters for configuring the creation operation
        :return:
        """
        ...

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
