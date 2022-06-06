# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: test_persistent_dict.py 
@time: 2022/05/11
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description:
@note:
1. In tests, if the persistent dictionary is closed on the way, it MUST RELOAD it at the end.
2. If a key is deleted midway, it MUST DELETE the corresponding value in the self.current_keys array.
"""
import os
import random
import unittest
import threading

from data_persistence.interfaces import PersistentBytesDict
from data_persistence.persistent_dict import PickledDict, DBMDict

_thread_lock = threading.Lock()


def _fake_dict(size: int, key_len: int, val_len: int) -> dict:
    return {os.urandom(key_len): os.urandom(val_len) for _ in range(size)}


def _reload_persistent_dict(dict_: PersistentBytesDict) -> PersistentBytesDict:
    dict_path = dict_.dict_local_path
    dict_.close()
    return type(dict_).open(dict_path)


def _need_reload(probability=0.5) -> bool:
    return random.random() >= (1 - probability)


def _compare_inmemory_dict_with_persistent_dict(inmemory_dict: dict,
                                                persistent_dict: PersistentBytesDict,
                                                need_randomly_reload: bool = False) -> bool:
    """
    :param inmemory_dict:
    :param persistent_dict:
    :param need_randomly_reload: if set to True, DO RELOAD THE PARAM persistent_array!!!
    The original dict may be released at a high probability.
    :return:
    """
    if len(inmemory_dict) != len(persistent_dict):
        return False

    for k in inmemory_dict.keys():
        if need_randomly_reload and _need_reload(0.1):
            persistent_dict = _reload_persistent_dict(persistent_dict)

        if inmemory_dict[k] != persistent_dict[k]:
            return False
    return True


class TestPickledDict(unittest.TestCase):
    PersistentDictClass = PickledDict

    def setUp(self) -> None:
        self.test_dict_size = 1000
        self.test_dict_key_len = 16
        self.test_dict_val_len = 16

        self.test_persistent_dict_path = "test.dict"
        if os.path.exists(self.test_persistent_dict_path):
            os.remove(self.test_persistent_dict_path)

        self.inmemory_dict = _fake_dict(self.test_dict_size, self.test_dict_key_len, self.test_dict_val_len)
        self.persistent_dict = self.PersistentDictClass.from_dict(self.inmemory_dict, self.test_persistent_dict_path)
        self.current_keys = list(self.inmemory_dict)

    def tearDown(self) -> None:
        self.persistent_dict.release()

    def test_from_dict_firstly(self):
        self.assertTrue(_compare_inmemory_dict_with_persistent_dict(self.inmemory_dict, self.persistent_dict))

    def test_set_value(self):
        """ Test the correctness of the persistent dictionary `__setitem__`,
        which already contains the verification of `__getitem__` and `__len__`.
        """
        test_keys_num = 100
        test_keys = random.sample(self.current_keys, test_keys_num)

        for key in test_keys:
            new_value = os.urandom(self.test_dict_val_len)
            self.inmemory_dict[key] = new_value
            self.persistent_dict[key] = new_value

        self.assertTrue(_compare_inmemory_dict_with_persistent_dict(self.inmemory_dict, self.persistent_dict))

        # reload
        self.persistent_dict = _reload_persistent_dict(self.persistent_dict)
        # check again
        self.assertTrue(_compare_inmemory_dict_with_persistent_dict(self.inmemory_dict, self.persistent_dict))

    def test_set_value2(self):
        """ Test in more extreme cases
        where persistent dictionaries are opened, closed and synced multiple times
        """
        test_keys_num = 100
        test_keys = random.sample(self.current_keys, test_keys_num)

        for key in test_keys:
            new_value = os.urandom(self.test_dict_val_len)
            self.inmemory_dict[key] = new_value
            if _need_reload():
                self.persistent_dict = _reload_persistent_dict(self.persistent_dict)
            self.persistent_dict[key] = new_value

        self.assertTrue(_compare_inmemory_dict_with_persistent_dict(self.inmemory_dict,
                                                                    self.persistent_dict,
                                                                    need_randomly_reload=True))
        # Finally, reload the persistent dict!!!
        self.persistent_dict = _reload_persistent_dict(self.persistent_dict)

    def test_contains(self):
        """ Test the correctness of the persistent dictionary `__contains__`
        """
        random_key_to_test = 100

        for key in self.current_keys:
            self.assertTrue(key in self.persistent_dict)

        for _ in range(random_key_to_test):
            rand_key = os.urandom(self.test_dict_key_len)
            self.assertTrue((rand_key in self.inmemory_dict) == (rand_key in self.persistent_dict))

    def test_contains2(self):
        random_key_to_test = 100

        for key in self.current_keys:
            self.assertTrue(key in self.persistent_dict)
            if _need_reload(0.1):
                self.persistent_dict = _reload_persistent_dict(self.persistent_dict)

        for _ in range(random_key_to_test):
            rand_key = os.urandom(self.test_dict_key_len)
            self.assertTrue((rand_key in self.inmemory_dict) == (rand_key in self.persistent_dict))
            if _need_reload(0.1):
                self.persistent_dict = _reload_persistent_dict(self.persistent_dict)

        # Finally, reload the persistent dict!!!
        self.persistent_dict = _reload_persistent_dict(self.persistent_dict)

    def test_iter(self):
        """ Test the correctness of the persistent dictionary `__iter__`
        """
        key_list_output_by_persistent_list = list(iter(self.persistent_dict))

        # Firstly, ensure that the lengths are equal
        self.assertEqual(len(self.inmemory_dict), len(key_list_output_by_persistent_list))

        for key in key_list_output_by_persistent_list:
            self.assertIn(key, self.inmemory_dict)

    def test_delete_item(self):
        """ Test the correctness of the persistent dictionary `__delitem__`
        """
        test_keys_num = 100
        test_keys = random.sample(self.current_keys, test_keys_num)

        for key in test_keys:
            del self.persistent_dict[key]
            del self.inmemory_dict[key]
            self.current_keys.remove(key)

        self.assertTrue(_compare_inmemory_dict_with_persistent_dict(self.inmemory_dict, self.persistent_dict))

        # reload
        self.persistent_dict = _reload_persistent_dict(self.persistent_dict)
        # check again
        self.assertTrue(_compare_inmemory_dict_with_persistent_dict(self.inmemory_dict, self.persistent_dict))

    def test_delete_item2(self):
        """ Test the correctness of the persistent dictionary `__delitem__`
        where persistent dictionaries are opened, closed and synced multiple times
        """
        test_keys_num = 100
        test_keys = random.sample(self.current_keys, test_keys_num)

        for key in test_keys:
            del self.persistent_dict[key]
            del self.inmemory_dict[key]
            if _need_reload():
                self.persistent_dict = _reload_persistent_dict(self.persistent_dict)
            self.current_keys.remove(key)

        self.assertTrue(_compare_inmemory_dict_with_persistent_dict(self.inmemory_dict,
                                                                    self.persistent_dict,
                                                                    need_randomly_reload=True))

        # Finally, reload the persistent dict!!!
        self.persistent_dict = _reload_persistent_dict(self.persistent_dict)

    def _test_closed_persistent_dict(self):
        """ Internal test function, MAKE SURE that self.persistent_array is closed at this time
        """
        with self.assertRaisesRegex(ValueError, "closed"):
            self.persistent_dict[os.urandom(self.test_dict_key_len)] = b"3"

        with self.assertRaisesRegex(ValueError, "closed"):
            _ = self.persistent_dict[self.current_keys[0]]

        with self.assertRaisesRegex(ValueError, "closed"):
            _ = len(self.persistent_dict)

        with self.assertRaisesRegex(ValueError, "closed"):
            del self.persistent_dict[self.current_keys[0]]

        with self.assertRaisesRegex(ValueError, "closed"):
            _ = iter(self.persistent_dict)

    def test_close(self):
        self.persistent_dict.close()
        self._test_closed_persistent_dict()
        # reload
        self.persistent_dict = _reload_persistent_dict(self.persistent_dict)
        rand_key = os.urandom(self.test_dict_key_len)
        rand_val = os.urandom(self.test_dict_val_len)

        self.persistent_dict[rand_key] = rand_val
        self.inmemory_dict[rand_key] = rand_val

        # __setitem__, __getitem__, __len__
        self.assertTrue(_compare_inmemory_dict_with_persistent_dict(self.inmemory_dict, self.persistent_dict))

        # __delitem__
        del self.persistent_dict[rand_key]
        del self.inmemory_dict[rand_key]
        self.assertTrue(_compare_inmemory_dict_with_persistent_dict(self.inmemory_dict, self.persistent_dict))

        # __iter__
        self.test_iter()

    def test_context(self):
        self.persistent_dict.close()  # close current persistent dict firstly
        with self.PersistentDictClass.open(self.test_persistent_dict_path) as self.persistent_dict:
            pass

        # test closed persistent dict
        self._test_closed_persistent_dict()

    def test_exceptions(self):
        """ Test if the array throws an exception as expected:
        * `FileNotFoundError` when read a not-existent array
        * `FileExistsError` when create an array of which the local file path is already occupied.
        * `TypeError` when create an array but mode code is not valid (not 'r' or 'c')
        * `TypeError` when write a not byte-like object to the array
        * `ValueError` when the length of the bytes to write is greater than the item length of the array
        * `ValueError` when the array is closed (not test here).
        * `KeyError` when the key not exists
        """
        with self.assertRaises(FileNotFoundError):
            _ = self.PersistentDictClass.open("path_not_exists")
        with self.assertRaises(FileExistsError):
            # already created
            _ = self.PersistentDictClass.create(self.test_persistent_dict_path)

        # `TypeError` when create an array but mode code is not valid (not 'r' or 'c')
        invalid_mode_code = "w"
        with self.assertRaisesRegex(TypeError, f"Unexpected Mode: {invalid_mode_code}"):
            _ = self.PersistentDictClass("valid_path", invalid_mode_code)

        # `TypeError` when write a not byte-like object to the array
        # # Writing string is invalid
        with self.assertRaisesRegex(TypeError, "The content should be a byte string."):
            self.persistent_dict[self.current_keys[0]] = "writing string is invalid"

        # # Writing Integer is valid
        with self.assertRaisesRegex(TypeError, "The content should be a byte string."):
            self.persistent_dict[self.current_keys[0]] = 11111

        # KeyError
        test_num = 10
        for _ in range(test_num):
            rand_key = os.urandom(self.test_dict_key_len)
            if rand_key not in self.current_keys:
                with self.assertRaises(KeyError):
                    _ = self.persistent_dict[rand_key]
                self.assertEqual(self.persistent_dict.get(rand_key, 1000), 1000)


class TestDBMDict(TestPickledDict):
    PersistentDictClass = DBMDict
