# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: test_persistent_array.py
@time: 2022/05/31
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description:
@note:
1. In tests, if the persistent list is closed on the way, it MUST RELOAD it at the end.
2. If an item is deleted midway, it MUST SET the corresponding value in the self.current_keys array TO ALL-ZERO BYTES.
@todo:
1. use with statement for each sub-test! (所有测试不要共用一个测试数组了)
"""
import operator
import os
import random
import typing
import unittest

from data_persistence.interfaces import PersistentFixedLengthBytesArray
from data_persistence.persistent_array import SPFLBArray
from test.tools.slice_test_tools import COMMON_SLICE_TEST_CASES, generate_random_slice, calc_slice_len


def _fake_array(size: int, item_size: int) -> list:
    return [os.urandom(item_size) for _ in range(size)]


def _reload_persistent_array(arr: PersistentFixedLengthBytesArray) -> PersistentFixedLengthBytesArray:
    array_path = arr.local_path
    arr.close()
    return type(arr).open(array_path)


def _need_reload(probability=0.5) -> bool:
    return random.random() >= (1 - probability)


def _compare_inmemory_array_with_persistent_array(inmemory_list: typing.List[bytes],
                                                  persistent_array: PersistentFixedLengthBytesArray,
                                                  need_randomly_reload: bool = False) -> bool:
    """
    :param inmemory_list:
    :param persistent_array:
    :param need_randomly_reload: if set to True, DO RELOAD THE PARAM persistent_array!!!
    The original dict may be released at a high probability.
    :return:
    """
    if len(inmemory_list) != len(persistent_array):
        return False

    for k, item in enumerate(inmemory_list):
        if need_randomly_reload and _need_reload(0.1):
            persistent_array = _reload_persistent_array(persistent_array)

        if item != persistent_array[k]:
            return False
    return True


def _yield_random_bytes(bytes_len_range: typing.Tuple[int, int],
                        iter_num_range: typing.Tuple[int, int]) -> typing.Iterable[bytes]:
    """ Create an iterator with the number of iterations randomly selected in the closed interval `iter_num_range`
    and the byte length of the yield randomly selected in the closed interval `bytes_len_range`
    """
    bytes_len_lower_bound, bytes_len_upper_bound = bytes_len_range
    iter_num_lower_bound, iter_num_upper_bound = iter_num_range
    iter_num = random.randint(iter_num_lower_bound, iter_num_upper_bound)

    for _ in range(iter_num):
        bytes_len = random.randint(bytes_len_lower_bound, bytes_len_upper_bound)
        yield os.urandom(bytes_len)


class TestSPFLBArray(unittest.TestCase):
    PersistentArrayClass = SPFLBArray

    def setup_array(self):
        self.inmemory_array = _fake_array(self.test_array_size, self.test_array_item_size)
        self.persistent_array = self.PersistentArrayClass.from_list(self.inmemory_array,
                                                                    self.test_persistent_array_path)

    def release_array(self):
        self.persistent_array.release()
        self.inmemory_array = []

    def setUp(self) -> None:
        self.test_array_size = 1000
        self.test_array_item_size = 16
        self.test_array_chunk_size = 100  # item num in each chunk -- item_num_in_one_file

        self.test_persistent_array_path = "test.array"
        if os.path.exists(self.test_persistent_array_path):
            raise ValueError("test array already exists")

        self.setup_array()

    def tearDown(self) -> None:
        self.release_array()

    def test_from_dict_firstly(self):
        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))
        self.assertEqual(self.persistent_array.local_path, self.test_persistent_array_path)
        self.assertEqual(self.persistent_array.item_size, self.test_array_item_size)

    def test_set_value(self):
        """ Test the correctness of the persistent dictionary `__setitem__`,
        which already contains the verification of `__getitem__` and `__len__`.
        """
        test_num = 100

        for _ in range(test_num):
            target_index = random.randint(0, self.test_array_size - 1)
            new_value = os.urandom(self.test_array_item_size)
            self.inmemory_array[target_index] = new_value
            self.persistent_array[target_index] = new_value

        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))

        # reload
        self.persistent_array = _reload_persistent_array(self.persistent_array)
        # check again
        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))

    def test_set_value2(self):
        """ Test in more extreme cases
        where persistent dictionaries are opened, closed and synced multiple times
        """
        test_num = 100

        for _ in range(test_num):
            target_index = random.randint(0, self.test_array_size - 1)
            new_value = os.urandom(self.test_array_item_size)
            self.inmemory_array[target_index] = new_value
            if _need_reload():
                self.persistent_array = _reload_persistent_array(self.persistent_array)
            self.persistent_array[target_index] = new_value

        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array,
                                                                      need_randomly_reload=True))
        # Finally, reload the persistent array!!!
        # Because the original self.persistent_array has been closed and the newly
        # opened array passed to _compare_inmemory_array_with_persistent_array is not assigned to it
        self.persistent_array = _reload_persistent_array(self.persistent_array)

    def test_set_value3(self):
        """ Consider the more common case: the value may be less than the fixed length
        (when the program needs to be preceded by leading zero bytes)
        or greater than the fixed length (when the program needs to throw an exception)
        """
        test_num = 100

        for _ in range(test_num):
            target_index = random.randint(0, self.test_array_size - 1)
            target_item_size = random.randint(0, self.test_array_item_size + 5)
            new_value = os.urandom(target_item_size)
            if target_item_size <= self.test_array_item_size:
                # padding
                self.inmemory_array[target_index] = b"\x00" * (self.test_array_item_size - target_item_size) + new_value
                self.persistent_array[target_index] = new_value
            else:  # will raise a ValueError
                with self.assertRaisesRegex(ValueError, "greater than"):
                    self.persistent_array[target_index] = new_value

        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))

        # reload
        self.persistent_array = _reload_persistent_array(self.persistent_array)
        # check again
        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))

    def test_contains(self):
        """ Test the correctness of the persistent dictionary `__contains__`
        """
        random_item_num_to_test = 100

        for item in self.inmemory_array:
            self.assertTrue(item in self.persistent_array)

        for _ in range(random_item_num_to_test):
            rand_item = os.urandom(self.test_array_item_size)
            self.assertTrue((rand_item in self.inmemory_array) == (rand_item in self.persistent_array))

    def test_contains2(self):
        random_item_num_to_test = 100

        for item in self.inmemory_array:
            self.assertTrue(item in self.persistent_array)
            if _need_reload(0.1):
                self.persistent_array = _reload_persistent_array(self.persistent_array)

        for _ in range(random_item_num_to_test):
            rand_item = os.urandom(self.test_array_item_size)
            self.assertTrue((rand_item in self.inmemory_array) == (rand_item in self.persistent_array))

            if _need_reload(0.1):
                self.persistent_array = _reload_persistent_array(self.persistent_array)

        # Finally, reload the persistent array!!!
        self.persistent_array = _reload_persistent_array(self.persistent_array)

    def test_iter(self):
        """ Test the correctness of the persistent dictionary `__iter__`
        """
        item_list_output_by_persistent_list_iter = list(iter(self.persistent_array))

        # Firstly, ensure that the lengths are equal
        self.assertEqual(len(self.inmemory_array), len(item_list_output_by_persistent_list_iter))

        for key in item_list_output_by_persistent_list_iter:
            self.assertIn(key, self.inmemory_array)

    def test_delete_item(self):
        """ Test the correctness of the persistent dictionary `__delitem__`
        """
        test_items_num = 100

        for _ in range(test_items_num):
            target_index = random.randint(0, self.test_array_size - 1)
            del self.persistent_array[target_index]
            # it's not actually deletion, set the target item to all-zero bytes
            self.inmemory_array[target_index] = b"\x00" * self.test_array_item_size

        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))

        # reload
        self.persistent_array = _reload_persistent_array(self.persistent_array)
        # check again
        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))

    def test_delete_item2(self):
        """ Test the correctness of the persistent dictionary `__delitem__`
        where persistent dictionaries are opened, closed and synced multiple times
        """
        test_items_num = 100

        for _ in range(test_items_num):
            target_index = random.randint(0, self.test_array_size - 1)
            del self.persistent_array[target_index]
            # it's not actually deletion, set the target item to all-zero bytes
            self.inmemory_array[target_index] = b"\x00" * self.test_array_item_size
            if _need_reload():
                self.persistent_array = _reload_persistent_array(self.persistent_array)

        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array,
                                                                      need_randomly_reload=True))

        # Finally, reload the persistent array!!!
        self.persistent_array = _reload_persistent_array(self.persistent_array)

    def _test_closed_persistent_dict(self):
        """ Internal test function, MAKE SURE that self.persistent_array is closed at this time
        """
        with self.assertRaisesRegex(ValueError, "closed"):
            self.persistent_array[random.randint(0, self.test_array_size - 1)] = b"3"

        with self.assertRaisesRegex(ValueError, "closed"):
            _ = self.persistent_array[random.randint(0, self.test_array_size - 1)]

        with self.assertRaisesRegex(ValueError, "closed"):
            _ = len(self.persistent_array)

        with self.assertRaisesRegex(ValueError, "closed"):
            del self.persistent_array[random.randint(0, self.test_array_size - 1)]

        with self.assertRaisesRegex(ValueError, "closed"):
            _ = iter(self.persistent_array)

    def test_close(self):
        self.persistent_array.close()
        self._test_closed_persistent_dict()
        # reload
        self.persistent_array = _reload_persistent_array(self.persistent_array)
        rand_index = random.randint(0, self.test_array_size - 1)
        rand_val = os.urandom(self.test_array_item_size)

        self.persistent_array[rand_index] = rand_val
        self.inmemory_array[rand_index] = rand_val

        # __setitem__, __getitem__, __len__
        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))

        # __delitem__
        del self.persistent_array[rand_index]
        self.inmemory_array[rand_index] = b"\x00" * self.test_array_item_size
        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))

        # __iter__
        self.test_iter()

    def test_context(self):
        self.persistent_array.close()  # close current persistent array firstly
        with self.PersistentArrayClass.open(self.test_persistent_array_path) as self.persistent_array:
            pass

        # test closed persistent array
        self._test_closed_persistent_dict()

        # Finally, reload the array
        self.persistent_array = _reload_persistent_array(self.persistent_array)

    def test_get_item_slice_version(self):
        """ Test whether __getitem__ of an array operate as expected when accepting slice as an argument
        """
        # common test
        for test_case in COMMON_SLICE_TEST_CASES:
            slice_ = slice(*test_case)
            self.assertEqual(self.persistent_array[slice_], self.inmemory_array[slice_])
        # random test
        random_test_num_per_scenario = 100

        index_range = (0, self.test_array_size - 1)
        stride_range = (-5, 5)

        # 8 possible scenarios, we use 3 bits to denote each scenario:
        # The less significant bit indicates whether the start value is None;
        # The second bit indicates whether the end value is None;
        # The most significant bit indicates whether the stride value is None.
        # For example:
        # 001 -> The start value is None, and the other two are not None.
        # 011 -> The start value and end value are None, and the stride value is not None
        # ...
        for scenario_num in range(0, 7):  # 0b111 -> arr[:::], is already checked
            is_start_None = bool(scenario_num & 0b001)
            is_end_None = bool(scenario_num & 0b010)
            is_stride_None = bool(scenario_num & 0b100)

            for _ in range(random_test_num_per_scenario):
                test_slice = generate_random_slice(index_range, stride_range,
                                                   is_start_None, is_end_None, is_stride_None)
                self.assertEqual(self.persistent_array[test_slice],
                                 self.inmemory_array[test_slice])

    def _mock_setitem_slice_version_like_persistent_array(self,
                                                          list_: typing.List[bytes],
                                                          slice_: slice,
                                                          vals: typing.Iterable[bytes]):
        """ Assign an iterable object to a python native list as directed by slice,
        based on the procedure of the `__setitem__` method of the persistent array.
        Because the native list's `__setitem__` method takes a different approach to assigning slice
        and iterable values than `persistent_array`.
        """
        start, stop, stride = slice_.indices(len(list_))
        vals_iter = iter(vals)
        try:
            for index in range(start, stop, stride):
                value = next(vals_iter)
                if len(value) > self.test_array_item_size:
                    raise ValueError(
                        "The length of the data to be written is greater than the item length of the persistent array"
                    )
                # padding
                value = b"\x00" * (self.test_array_item_size - len(value)) + value
                list_[index] = value
        except StopIteration:
            pass

    def test_set_item_slice_version(self):
        """ Test whether __setitem__ of an array operate as expected when accepting slice as an argument
        """
        # length bounds for iterable objects: [slice_len - iter_bound[0], slice_len - iter_bound[1]]
        # Since the length of the slice is not known, `iter_bound` only defines relative offsets
        iter_bound_offset = (-5, 5)

        # new item size bound: [new_item_size_bound[0], new_item_size_bound[1]]
        new_item_size_bound = (self.test_array_item_size - 5, self.test_array_item_size)

        ###############
        # common test #
        ###############
        for test_case in COMMON_SLICE_TEST_CASES:
            slice_ = slice(*test_case)
            slice_len = calc_slice_len(slice_, len(self.persistent_array))
            actual_iter_bound = (slice_len + iter_bound_offset[0],
                                 slice_len + iter_bound_offset[1])

            # DO NOT USE generator DIRECTLY! It will output different values for two arrays.
            val_list = list(_yield_random_bytes(
                new_item_size_bound,
                actual_iter_bound
            ))

            self.persistent_array[slice_] = val_list
            self._mock_setitem_slice_version_like_persistent_array(self.inmemory_array, slice_, val_list)

            # check target slice for each case
            self.assertEqual(self.persistent_array[slice_], self.inmemory_array[slice_])
            # check whole array for each case
            self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))

        ###############
        # random test #
        ###############
        random_test_num_per_scenario = 100

        slice_index_range = (0, self.test_array_size - 1)
        slice_stride_range = (-5, 5)

        for scenario_num in range(0, 7):  # 0b111 -> arr[:::], is already checked
            is_start_None = bool(scenario_num & 0b001)
            is_end_None = bool(scenario_num & 0b010)
            is_stride_None = bool(scenario_num & 0b100)

            for _ in range(random_test_num_per_scenario):
                test_slice = generate_random_slice(slice_index_range, slice_stride_range,
                                                   is_start_None, is_end_None, is_stride_None)
                slice_len = calc_slice_len(test_slice, len(self.persistent_array))

                actual_iter_bound = (slice_len + iter_bound_offset[0],
                                     slice_len + iter_bound_offset[1])

                val_list = list(_yield_random_bytes(
                    new_item_size_bound,
                    actual_iter_bound
                ))

                self.persistent_array[test_slice] = val_list
                self._mock_setitem_slice_version_like_persistent_array(self.inmemory_array, test_slice, val_list)

                # check target slice for each case
                self.assertEqual(self.persistent_array[test_slice], self.inmemory_array[test_slice])
                # check whole array for each case
                self.assertTrue(
                    _compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))

    def _mock_delitem_slice_version_like_persistent_array(self,
                                                          list_: typing.List[bytes],
                                                          slice_: slice):
        """ delete multiple items from a python native list as directed by slice,
        based on the procedure of the `__setitem__` method of the persistent array.
        """
        start, stop, stride = slice_.indices(len(list_))

        for index in range(start, stop, stride):
            list_[index] = b"\x00" * self.test_array_item_size

    def test_del_item_slice_version(self):
        """ Test whether __delitem__ of an array operate as expected when accepting slice as an argument
        Unlike the previous test, you need to recreate the array for each sample,
        because the delete operation will result in zero bytes, and if you don't recreate the array,
        the subsequent arrays will most likely be composed of all zero bytes
        """
        self.release_array()

        ###############
        # common test #
        ###############
        for test_case in COMMON_SLICE_TEST_CASES:
            self.setup_array()
            slice_ = slice(*test_case)

            del self.persistent_array[slice_]
            self._mock_delitem_slice_version_like_persistent_array(self.inmemory_array, slice_)

            # check target slice for each case
            self.assertEqual(self.persistent_array[slice_], self.inmemory_array[slice_])
            # check whole array for each case
            self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))
            self.release_array()

        ###############
        # random test #
        ###############
        random_test_num_per_scenario = 100

        slice_index_range = (0, self.test_array_size - 1)
        slice_stride_range = (-5, 5)

        for scenario_num in range(0, 7):  # 0b111 -> arr[:::], is already checked

            is_start_None = bool(scenario_num & 0b001)
            is_end_None = bool(scenario_num & 0b010)
            is_stride_None = bool(scenario_num & 0b100)

            for _ in range(random_test_num_per_scenario):
                self.setup_array()

                test_slice = generate_random_slice(slice_index_range, slice_stride_range,
                                                   is_start_None, is_end_None, is_stride_None)

                del self.persistent_array[test_slice]
                self._mock_delitem_slice_version_like_persistent_array(self.inmemory_array, test_slice)

                # check target slice for each case
                self.assertEqual(self.persistent_array[test_slice], self.inmemory_array[test_slice])
                # check whole array for each case
                self.assertTrue(
                    _compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))
                self.release_array()

    def test_exceptions(self):
        """ Test if the array throws an exception as expected:
        * `FileNotFoundError` when read a not-existent array
        * `FileExistsError` when create an array of which the local file path is already occupied.
        * `ValueError` when the meta file is not valid
        * `TypeError` when create an array but some argument is missing
        * `TypeError` when create an array but mode code is not valid (not 'r' or 'c')
        * `TypeError` when write a not byte-like object to the array
        * Index out of range
        * `ValueError` when the length of the bytes to write is greater than the item length of the array
        * `ValueError` when the array is closed (not test here).
        """
        with self.assertRaises(FileNotFoundError):
            _ = self.PersistentArrayClass.open("path_not_exists")
        with self.assertRaises(FileExistsError):
            # already created
            _ = self.PersistentArrayClass.create(self.test_persistent_array_path,
                                                 item_size=16,
                                                 array_len=1000,
                                                 item_num_in_one_file=100)
        import pickle
        # meta param is not a tuple
        invalid_params = "invalid"  # may be a string...
        invalid_path = "invalid"
        invalid_meta_filepath = invalid_path + "_meta"
        with open(invalid_meta_filepath, "wb") as f:
            pickle.dump(invalid_params, f)

        with self.assertRaisesRegex(ValueError, r"The meta file (.*?) is broken"):
            _ = self.PersistentArrayClass.open(invalid_path)

        invalid_params = [16, 1000, 100]  # may be a list...
        with open(invalid_meta_filepath, "wb") as f:
            pickle.dump(invalid_params, f)

        with self.assertRaisesRegex(ValueError, r"The meta file (.*?) is broken"):
            _ = self.PersistentArrayClass.open(invalid_path)

        # some meta param is not a integer
        invalid_params = (16, '1000', 100)
        with open(invalid_meta_filepath, "wb") as f:
            pickle.dump(invalid_params, f)

        with self.assertRaisesRegex(ValueError, r"The meta file (.*?) is broken"):
            _ = self.PersistentArrayClass.open(invalid_path)

        # `TypeError` when create an array but some argument is missing
        # todo use permutations
        with self.assertRaisesRegex(TypeError, r"Missing parameters: array_len, item_num_in_one_file"):
            _ = self.PersistentArrayClass.create("valid_path",
                                                 item_size=100)

        with self.assertRaisesRegex(TypeError, r"Missing parameters: item_num_in_one_file"):
            _ = self.PersistentArrayClass.create("valid_path",
                                                 array_len=100,
                                                 item_size=100)

        # `TypeError` when create an array but mode code is not valid (not 'r' or 'c')
        invalid_mode_code = "w"
        with self.assertRaisesRegex(TypeError, f"Unexpected Mode: {invalid_mode_code}"):
            _ = self.PersistentArrayClass("valid_path", invalid_mode_code, param1='param1')

        # `TypeError` when write a not byte-like object to the array
        # # Writing string is invalid
        with self.assertRaisesRegex(TypeError, "The content should be a byte string."):
            self.persistent_array[0] = "writing string is invalid"

        # # Writing Integer is valid
        with self.assertRaisesRegex(TypeError, "The content should be a byte string."):
            self.persistent_array[0] = 11111

        # Index out of range
        with self.PersistentArrayClass.create("temp_array", item_size=16, item_num_in_one_file=100,
                                              array_len=1000) as tmp_arr:
            tmp_arr[1] = b"valid_pos"
            with self.assertRaisesRegex(IndexError, "out of range"):
                tmp_arr[1001] = b"invalid_pos"
            tmp_arr[-1] = b"valid_pos"
            tmp_arr[-1000] = b"valid_pos"
            with self.assertRaisesRegex(IndexError, "out of range"):
                tmp_arr[-1001] = b"invalid_pos"
            tmp_arr.release()

        # `ValueError` when the length of the bytes to write is greater than the item length of the array
        item_size = 16
        test_num = 10
        array_len = 1000

        with self.PersistentArrayClass.create("temp_array", item_size=16, item_num_in_one_file=100,
                                              array_len=1000) as tmp_arr:
            for _ in range(test_num):
                test_item = os.urandom(random.randint(item_size - 5, item_size + 5))
                random_index = random.randint(0, array_len - 1)
                if len(test_item) > item_size:
                    with self.assertRaisesRegex(ValueError, "greater than"):
                        tmp_arr[random_index] = test_item
                else:
                    tmp_arr[random_index] = test_item
            tmp_arr.release()

        # clear up
        if os.path.exists(invalid_meta_filepath):
            os.unlink(invalid_meta_filepath)

    def test_negative_index(self):
        """  Tests if negative indexes work as expected.
        Exceptions are not tested here (already in test_exceptions).
        """
        test_num = 100
        for _ in range(test_num):
            random_neg_index = random.randint(-self.test_array_size, -1)
            actual_pos_index = random_neg_index + self.test_array_size

            # cross-check
            self.assertEqual(self.persistent_array[random_neg_index],
                             self.persistent_array[actual_pos_index])

            self.assertEqual(self.persistent_array[random_neg_index],
                             self.inmemory_array[random_neg_index])

            del self.persistent_array[random_neg_index]
            self.inmemory_array[random_neg_index] = b"\x00" * self.test_array_item_size

            self.assertEqual(self.persistent_array[random_neg_index],
                             self.persistent_array[actual_pos_index])

            self.assertEqual(self.persistent_array[random_neg_index],
                             self.inmemory_array[random_neg_index])

            new_item = os.urandom(self.test_array_item_size)
            self.persistent_array[random_neg_index] = new_item
            self.inmemory_array[random_neg_index] = new_item

            self.assertEqual(self.persistent_array[random_neg_index],
                             self.persistent_array[actual_pos_index])

            self.assertEqual(self.persistent_array[random_neg_index],
                             self.inmemory_array[random_neg_index])

    def test_rollback(self):
        test_slice = slice(0, 100, None)
        test_items = list(_yield_random_bytes((self.test_array_item_size - 5, self.test_array_item_size),
                                              (101, 101)))
        test_items[88] = os.urandom(self.test_array_item_size + 3)  # invalid
        with self.assertRaisesRegex(ValueError, "greater than"):
            self.persistent_array[test_slice] = test_items

        self.assertTrue(_compare_inmemory_array_with_persistent_array(self.inmemory_array, self.persistent_array))
