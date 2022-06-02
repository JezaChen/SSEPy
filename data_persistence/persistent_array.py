# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: persistent_array.py
@time: 2022/05/11
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import collections.abc
import math
import operator
import os.path
import typing

from data_persistence.interfaces import PersistentFixedLengthBytesArray
import pickle

__all__ = ["SPFLBArray"]


class _ClosedDescriptor:
    def __init__(self, error_msg: str):
        self.__error_msg = error_msg

    def __get__(self, obj, obj_type=None):
        raise ValueError(self.__error_msg)

    def __set__(self, instance, value):
        raise ValueError(self.__error_msg)


class _ClosedFixedLengthBytesArray(collections.abc.Sequence):
    """Marker for a closed fixed-length bytes array. Access attempts raise a ValueError."""

    def closed(self, *args):
        raise ValueError('invalid operation on fixed-length bytes closed array')

    __iter__ = __len__ = __getitem__ = __setitem__ = release = close = closed
    item_size = local_path = _ClosedDescriptor('invalid operation on fixed-length bytes closed array')

    def __repr__(self):
        return '<Closed Fixed-Length Bytes Array>'


class SimpleMultiFilePersistentFixedLengthBytesArray(collections.abc.Sequence):
    """ A persistent fixed-length array storing in multiple binary files.

    - File Format:
        * Meta File: local_path + "_" + "meta"
        * Chunk File: local_path + "_" + file_id (int)
    - Meta File: Store some metadata:
        * item_size: the size of item (bytes)
        * array_len: the length of the persistent array
        * item_num_in_one_file: the number of items stored in one file
    """

    @typing.overload
    def __init__(self,
                 file_path: str,
                 mode: str = "r"):
        ...

    @typing.overload
    def __init__(self,
                 file_path: str,
                 mode: str = "c",
                 *,
                 item_size: int,
                 array_len: int,
                 item_num_in_one_file: int):
        ...

    def __init__(self,
                 local_path: str,
                 mode: str = "r",
                 **kwargs
                 ):
        self.__local_path = local_path

        if mode == "r":  # read
            # Open Meta file
            try:
                meta_file = open(local_path + "_meta", "rb+")
            except FileNotFoundError:
                raise FileNotFoundError(f"The meta file corresponding to the local path {local_path} not exists.")
            # Try read metadata from meta file
            try:
                pickled_object = pickle.load(meta_file)
                # check `pickled_object` is a valid tuple of which length is 3 and its elements are integers
                if isinstance(pickled_object, typing.Tuple) and len(pickled_object) == 3:
                    self.__item_size, self.__array_len, self.__item_num_in_one_file = pickled_object
                else:
                    raise ValueError(f"The meta file corresponding to the local path {local_path} is broken.")

                if not (isinstance(self.__item_size, int) and isinstance(self.__array_len, int) and isinstance(
                        self.__item_num_in_one_file, int)):
                    raise ValueError(f"The meta file corresponding to the local path {local_path} is broken.")
            except pickle.UnpicklingError:
                raise ValueError(f"The meta file corresponding to the local path {local_path} is broken.")
            finally:
                meta_file.close()

        elif mode == "c":  # create
            if os.path.exists(self.__local_path + "_meta"):
                raise FileExistsError(f"The file {local_path} exists, and you set the parameter create_only to True.")
            meta_file = open(local_path + "_meta", "wb+")

            # Parse Argument
            try:
                self.__item_size = int(kwargs["item_size"])
                self.__array_len = int(kwargs["array_len"])
                self.__item_num_in_one_file = int(kwargs["item_num_in_one_file"])
            except KeyError as exc:
                meta_file.close()
                raise TypeError(
                    f"When mode='c', the constructor is missing parameters: {', '.join(param for param in exc.args)}"
                )

            # Save meta file
            try:
                pickle.dump((self.__item_size, self.__array_len, self.__item_num_in_one_file),
                            meta_file)
            finally:
                meta_file.close()
        else:  # Unexpected mode
            raise TypeError(f"Unexpected Mode: {mode}")

        self.__file_num = math.ceil(self.__array_len / self.__item_num_in_one_file)
        self.__opened_files: typing.List[typing.Optional[typing.BinaryIO]] = [None] * self.__file_num

    def _get_file_by_id(self, file_id: int) -> typing.BinaryIO:
        if self.__opened_files[file_id] is not None:  # Caching
            return self.__opened_files[file_id]

        file_path = self.__local_path + f"_{file_id}"
        try:
            file = open(file_path, "rb+")
        except FileNotFoundError:
            file = open(file_path, "wb+")
        self.__opened_files[file_id] = file
        return file

    def _get_bytes_by_index(self, index: int) -> bytes:
        """ Find the corresponding file and offset according to the index indication, and read the data
        :return: If the returned byte length is 0 (empty byte),
        it means the content is empty and the caller needs to return all-zero bytes.
        """
        file_id, offset = divmod(index, self.__item_num_in_one_file)
        file = self._get_file_by_id(file_id)
        # offset_bytes is the offset of the file in bytes.
        offset_bytes = offset * self.__item_size
        file.seek(offset_bytes, 0)
        ret = file.read(self.__item_size)

        # The byte sequence read from the real file may be smaller than the item length
        # and needs to be padded with zero bytes
        ret += b"\x00" * (self.__item_size - len(ret))
        return ret

    def _write_bytes_to_file(self, index: int, content: bytes):
        if not isinstance(content, typing.ByteString):
            raise TypeError(
                "The content should be a byte string."
            )
        if len(content) > self.__item_size:
            raise ValueError(
                "The length of the data to be written is greater than the item length of the persistent array"
            )

        # padding
        content = b"\x00" * (self.__item_size - len(content)) + content

        file_id, offset = divmod(index, self.__item_num_in_one_file)
        file = self._get_file_by_id(file_id)
        # offset_bytes is the offset of the file in bytes.
        offset_bytes = offset * self.__item_size
        file.seek(offset_bytes, 0)
        file.write(content)

    def __getitem__(self, item: typing.Union[slice, int]) -> typing.Union[list[bytes], bytes]:
        """ Now, getting items by slices will return a list object,
        not persistent array!
        """
        # index: slice version
        if isinstance(item, slice):
            start, stop, stride = item.indices(len(self))
            ret = []
            for index in range(start, stop, stride):
                ret.append(self._get_bytes_by_index(index))
            return ret

        # index: int version
        index = operator.index(item)
        if index >= len(self) or index < -len(self):
            raise IndexError("Array index out of range")

        ret = self._get_bytes_by_index(index)
        return ret

    def __setitem__(self,
                    key: typing.Union[slice, int],
                    value: typing.Union[bytes, typing.Iterable[bytes]]):
        """ Write the value to the persistable array according to the parameter key's instructions
        * If the key is a slice, parameter value should be iterable
        The number of writes depends on the minimum of the actual number
        of elements in the slice and the length of the iterable parameter value.
        * If the key is an integer, the parameter value should be a byte-like object.
        """
        if isinstance(key, slice):
            value_iter = iter(value)  # value should be iterable

            start, stop, stride = key.indices(len(self))
            try:
                for index in range(start, stop, stride):
                    self._write_bytes_to_file(index, next(value_iter))
            except StopIteration:
                pass
            return
        index = operator.index(key)
        if index >= len(self) or index < -len(self):
            raise IndexError("Array index out of range")

        self._write_bytes_to_file(index, bytes(value))

    def __len__(self):
        return self.__array_len

    @property
    def item_size(self):
        return self.__item_size

    @property
    def local_path(self):
        return self.__local_path

    def release(self):
        # Firstly, close the files!
        self.close()
        # delete meta file
        meta_file_path = self.__local_path + "_meta"
        os.unlink(meta_file_path)
        # delete content file
        for chunk_file_id in range(self.__file_num):
            chunk_file_path = self.__local_path + f"_{chunk_file_id}"
            try:
                os.unlink(chunk_file_path)
            except FileNotFoundError:  # the chunk file may be not found
                pass

    def __repr__(self):
        return f"<SimpleMultiFilePersistentFixedLengthBytesArray local_path: {self.local_path}>"

    def closed(self, *args, **kwargs):
        raise ValueError('invalid operation on closed array')

    def close(self):
        for opened_file in self.__opened_files:
            if opened_file is not None:
                opened_file.close()


class SPFLBArray(PersistentFixedLengthBytesArray):
    """ Simple Persistent Fixed Length Bytes Array
    It is a simple persistent fixed-length array storing in multiple binary files without caching.
    It wraps a SimpleMultiFilePersistentFixedLengthBytesArray instance as its underlying list.
    """

    @classmethod
    def open(cls,
             local_path: str) -> 'SPFLBArray':
        return cls(local_path, mode="r")

    @classmethod
    def create(cls,
               local_path: str,
               **kwargs) -> 'SPFLBArray':

        try:
            item_size: int = kwargs["item_size"]
            array_len: int = kwargs["array_len"]
            item_num_in_one_file: int = kwargs["item_num_in_one_file"]
        except KeyError as exc:
            raise TypeError(f"Missing parameters: f{', '.join(param for param in exc.args)}")

        return cls(local_path,
                   mode="c",
                   item_size=item_size,
                   array_len=array_len,
                   item_num_in_one_file=item_num_in_one_file)

    @typing.overload
    def __init__(self,
                 file_path: str,
                 mode: str = "r"):
        ...

    @typing.overload
    def __init__(self,
                 file_path: str,
                 mode: str = "c",
                 *,
                 item_size: int,
                 array_len: int,
                 item_num_in_one_file: int):
        ...

    def __init__(self,
                 local_path: str,
                 mode: str = "r",
                 **kwargs
                 ):
        self.__local_path = local_path
        self.__underlying_array = SimpleMultiFilePersistentFixedLengthBytesArray(local_path, mode, **kwargs)

    def __getitem__(self, item: typing.Union[slice, int]) -> typing.Union[list[bytes], bytes]:
        return self.__underlying_array[item]

    def __setitem__(self,
                    key: typing.Union[slice, int],
                    value: typing.Union[bytes, typing.Iterable[bytes]]):
        self.__underlying_array[key] = value

    def __len__(self):
        return len(self.__underlying_array)

    def __iter__(self):
        # override the __iter__ method of the base class to return the iterator of the underlying array directly,
        # otherwise, getting the iterator after the underlying array is closed will not throw an exception.
        return iter(self.__underlying_array)

    def sync(self) -> None:
        """ Simple multi-file sustainable fixed-length byte arrays do not come with a cache,
         so the sync method is left empty.
        """
        pass

    @property
    def item_size(self):
        return self.__underlying_array.item_size

    @property
    def local_path(self):
        """ The underlying array is closed and the local_path feature is no longer available,
        so here it returns its own stored properties directly
        """
        return self.__local_path

    def release(self):
        try:
            self.__underlying_array.release()
        except (AttributeError, ValueError):  # release multiple times
            pass
        finally:
            try:
                self.__underlying_array = _ClosedFixedLengthBytesArray()
            except:
                self.__underlying_array = None

    def __repr__(self):
        try:
            return f"<SPFLBArray local_path: {self.local_path}>"
        except ValueError:
            return f"<SPFLBArray closed>"

    def close(self):
        try:
            self.__underlying_array.close()
        except (AttributeError, ValueError):  # self.__underlying_array is already a closed list
            pass
        finally:
            try:
                self.__underlying_array = _ClosedFixedLengthBytesArray()
            except:
                self.__underlying_array = None

    @classmethod
    def from_list(cls,
                  list_: list[bytes],
                  local_path: str,
                  *,
                  chunk_size: int = 100,
                  item_size: typing.Optional[int] = None,
                  list_len: typing.Optional[int] = None) -> 'SPFLBArray':
        """
        Create a fixed-length bytes array from a list.
        :param list_: List of bytes
        :param local_path: The local path to store the persistent array
        :param chunk_size: The number of items in one file (chunk)
        :param item_size: (Optional) the fixed size of item, if None, it will be the maximum value of all items in list.
        :param list_len: (Optional) the fixed length of array to create.
        If None, it will be the length of parameter `list_`.
        :return:
        """
        if item_size is None:
            item_size = max(len(item) for item in list_)

        if list_len is None:
            list_len = len(list_)
        list_len = max(list_len, len(list_))

        p_array = cls.create(local_path,
                             item_size=item_size,
                             array_len=list_len,
                             item_num_in_one_file=chunk_size)

        for index, item in enumerate(list_):
            extended_item = b"\x00" * (item_size - len(item)) + item
            p_array[index] = extended_item

        return p_array
