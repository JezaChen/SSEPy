# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: test_bits.py 
@time: 2022/03/12
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""

import unittest

from toolkit.bits import Bitset
from toolkit.bits_utils import half_bits


class TestBits(unittest.TestCase):
    def test_bits_class_len(self):
        test_list = [
            {
                "value": 0b11011,
                "length": 5,
                "fixed_length": False
            },
            {
                "value": 0b00000,
                "length": 0,
                "fixed_length": False
            },
            {
                "value": 0b00000,
                "length": 5,
                "fixed_length": True
            },
            {
                "value": 0b001001,
                "length": 6,
                "fixed_length": True
            }
        ]

        for case in test_list:
            value = case.get("value")
            length = case.get("length")
            fixed_length = case.get("fixed_length", False)

            if fixed_length:
                xbits = Bitset(value, length=length)
            else:
                xbits = Bitset(value)

            self.assertEqual(len(xbits), length)
            self.assertEqual(xbits.length, length)

    def test_bits_and_op(self):
        test_list = [
            {
                "a": Bitset(0b100101, 6),
                "b": Bitset(0b001001, 6),
                "r": Bitset(0b000001, 6)
            },
            {
                "a": Bitset(0b110100, 6),
                "b": Bitset(0b000010, 6),
                "r": Bitset(0b000000, 6)
            },
            {
                "a": Bitset(0b0011, 4),
                "b": Bitset(0b110001, 6),
                "r": Bitset(0b000001, 6)
            },
            {
                "a": Bitset(0b001110, 6),
                "b": Bitset(0b11, 2),
                "r": Bitset(0b000010, 6)
            }
        ]
        for case in test_list:
            a = case.get("a")
            b = case.get("b")
            r = case.get("r")
            self.assertEqual(a & b, r)

    def test_bits_or_op(self):
        test_list = [
            {
                "a": Bitset(0b100101, 6),
                "b": Bitset(0b001001, 6),
                "r": Bitset(0b101101, 6)
            },
            {
                "a": Bitset(0b110100, 6),
                "b": Bitset(0b000010, 6),
                "r": Bitset(0b110110, 6)
            },
            {
                "a": Bitset(0b0011, 4),
                "b": Bitset(0b110001, 6),
                "r": Bitset(0b110011, 6)
            },
            {
                "a": Bitset(0b001110, 6),
                "b": Bitset(0b11, 2),
                "r": Bitset(0b001111, 6)
            }
        ]
        for case in test_list:
            a = case.get("a")
            b = case.get("b")
            r = case.get("r")
            self.assertEqual(a | b, r)

    def test_bits_xor_op(self):
        test_list = [
            {
                "a": Bitset(0b100101, 6),
                "b": Bitset(0b001001, 6),
                "r": Bitset(0b101100, 6)
            },
            {
                "a": Bitset(0b110100, 6),
                "b": Bitset(0b000010, 6),
                "r": Bitset(0b110110, 6)
            },
            {
                "a": Bitset(0b0011, 4),
                "b": Bitset(0b110001, 6),
                "r": Bitset(0b110010, 6)
            },
            {
                "a": Bitset(0b001110, 6),
                "b": Bitset(0b11, 2),
                "r": Bitset(0b001101, 6)
            }
        ]
        for case in test_list:
            a = case.get("a")
            b = case.get("b")
            r = case.get("r")
            self.assertEqual(a ^ b, r)

    def test_bits_invert_op(self):
        test_list = [
            {
                "a": Bitset(0b100101, 6),
                "r": Bitset(0b011010, 6)
            },
            {
                "a": Bitset(0b110100, 6),
                "r": Bitset(0b001011, 6)
            },
            {
                "a": Bitset(0b00000000, 8),
                "r": Bitset(0b11111111, 8)
            },
            {
                "a": Bitset(0b11110000, 8),
                "r": Bitset(0b00001111, 8)
            },
        ]
        for case in test_list:
            a = case.get("a")
            r = case.get("r")
            self.assertEqual(r, ~a)

    def test_bits_xor_left_shift_op(self):
        test_list = [
            {
                "a": Bitset(0b001101, 6),
                "value": 2,
                "r": Bitset(0b110100, 6)
            },
            {
                "a": Bitset(0b001101, 6),
                "value": 3,
                "r": Bitset(0b101000, 6)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 4,
                "r": Bitset(0b01010000, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 8,
                "r": Bitset(0b00000000, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 0,
                "r": Bitset(0b00110101, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 9,
                "r": Bitset(0b00000000, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 11,
                "r": Bitset(0b00000000, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": -1,
                "r": "error"
            },
            {
                "a": Bitset(0b00110101),
                "value": 3,
                "r": Bitset(0b101000, 6)
            },
        ]

        for case in test_list:
            a = case.get("a")
            value = case.get("value")
            r = case.get("r")
            if r == "error":
                with self.assertRaises(ValueError):
                    a << value
            else:
                self.assertEqual(a << value, r)

    def test_bits_xor_right_shift_op(self):
        test_list = [
            {
                "a": Bitset(0b001101, 6),
                "value": 2,
                "r": Bitset(0b000011, 6)
            },
            {
                "a": Bitset(0b001101, 6),
                "value": 3,
                "r": Bitset(0b000001, 6)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 4,
                "r": Bitset(0b00000011, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 8,
                "r": Bitset(0b00000000, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 0,
                "r": Bitset(0b00110101, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 9,
                "r": Bitset(0b00000000, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 11,
                "r": Bitset(0b00000000, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": -1,
                "r": "error"
            },
            {
                "a": Bitset(0b00110101),
                "value": 3,
                "r": Bitset(0b000110, 6)
            },
        ]

        for case in test_list:
            a = case.get("a")
            value = case.get("value")
            r = case.get("r")
            if r == "error":
                with self.assertRaises(ValueError):
                    a >> value
            else:
                self.assertEqual(a >> value, r)

    def test_bits_get_higher_bits_method(self):
        test_list = [
            {
                "a": Bitset(0b001101, 6),
                "value": 2,
                "r": Bitset(0b00, 2)
            },
            {
                "a": Bitset(0b001101, 6),
                "value": 3,
                "r": Bitset(0b001, 3)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 4,
                "r": Bitset(0b0011, 4)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 8,
                "r": Bitset(0b00110101, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 0,
                "r": Bitset(0, 0)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 9,
                "r": "error"
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 11,
                "r": "error"
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": -1,
                "r": "error"
            },
            {
                "a": Bitset(0b00110101),
                "value": 3,
                "r": Bitset(0b110, 3)
            },
        ]

        for case in test_list:
            a = case.get("a")
            value = case.get("value")
            r = case.get("r")
            if r == "error":
                with self.assertRaises(ValueError):
                    a.get_higher_bits(value)
            else:
                self.assertEqual(a.get_higher_bits(value), r)

    def test_bits_get_lower_bits_method(self):
        test_list = [
            {
                "a": Bitset(0b001101, 6),
                "value": 2,
                "r": Bitset(0b01, 2)
            },
            {
                "a": Bitset(0b001101, 6),
                "value": 3,
                "r": Bitset(0b101, 3)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 4,
                "r": Bitset(0b0101, 4)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 8,
                "r": Bitset(0b00110101, 8)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 0,
                "r": Bitset(0, 0)
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 9,
                "r": "error"
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": 11,
                "r": "error"
            },
            {
                "a": Bitset(0b00110101, 8),
                "value": -1,
                "r": "error"
            },
            {
                "a": Bitset(0b00110101),
                "value": 3,
                "r": Bitset(0b101, 3)
            },
        ]

        for case in test_list:
            a = case.get("a")
            value = case.get("value")
            r = case.get("r")
            if r == "error":
                with self.assertRaises(ValueError):
                    a.get_lower_bits(value)
            else:
                self.assertEqual(a.get_lower_bits(value), r)

    def test_bits_half_method(self):
        test_list = [
            {
                "a": Bitset(0b001101, 6),
                "r": (Bitset(0b001, 3), Bitset(0b101, 3))
            },
            {
                "a": Bitset(0b00110101, 8),
                "r": (Bitset(0b0011, 4), Bitset(0b0101, 4))
            },
            {
                "a": Bitset(0b01, 2),
                "r": (Bitset(0b0, 1), Bitset(0b1, 1))
            },
            {
                "a": Bitset(0b1, 1),
                "r": (Bitset(0b0, 1), Bitset(0b1, 1))
            },
            {
                "a": Bitset(0b10001, 5),
                "r": (Bitset(0b010, 3), Bitset(0b001, 3))
            },
        ]

        for case in test_list:
            a = case.get("a")
            r = case.get("r")
            self.assertEqual(half_bits(a), r)

    def test_bits_add_op(self):
        test_list = [
            {
                "a": Bitset(0b100101, 6),
                "b": Bitset(0b001001, 6),
                "r": Bitset(0b100101001001, 12)
            },
            {
                "a": Bitset(0b110100, 6),
                "b": Bitset(0b000010, 6),
                "r": Bitset(0b110100000010, 12)
            },
            {
                "a": Bitset(0b0011, 4),
                "b": Bitset(0b110001, 6),
                "r": Bitset(0b0011110001, 10)
            },
            {
                "a": Bitset(0b001110, 6),
                "b": Bitset(0b11, 2),
                "r": Bitset(0b00111011, 8)
            },
            {
                "a": Bitset(0b001110, 6),
                "b": Bitset(0, 0),
                "r": Bitset(0b001110, 6)
            },
            {
                "a": Bitset(0, 0),
                "b": Bitset(0b001110, 6),
                "r": Bitset(0b001110, 6)
            }
        ]
        for case in test_list:
            a = case.get("a")
            b = case.get("b")
            r = case.get("r")
            self.assertEqual(a + b, r)

    def test_bits_to_bytes(self):
        test_list = [
            {
                "a": Bitset(0b001101, 6),
                "r": b"\x0d"
            },
            {
                "a": Bitset(0b00110101, 8),
                "r": b"\x35"
            },
            {
                "a": Bitset(0b01, 2),
                "r": b"\x01"
            },
            {
                "a": Bitset(0b0110110100111111, 16),
                "r": b"\x6d\x3f"
            },
            {
                "a": Bitset(0b10110100111111, 14),
                "r": b"\x2d\x3f"
            },
            {
                "a": Bitset(0b10110100111111, 32),
                "r": b"\x00\x00\x2d\x3f"
            }
        ]

        for case in test_list:
            a = case.get("a")
            r = case.get("r")
            self.assertEqual(bytes(a), r)

    def test_bits_from_bytes(self):
        test_list = [
            {
                "a": b"\x11\x3f\x12\x01",
                "length": 32,
                "r": Bitset(0b00010001001111110001001000000001, 32)
            },
            {
                "a": b"\xff",
                "length": 8,
                "r": Bitset(0b11111111)
            },
            {
                "a": b"\x01\xff",
                "r": Bitset(0b111111111, 9)
            },
            {
                "a": b"\x04\xff",
                "r": Bitset(0b10011111111, 11)
            },
            {
                "a": b"\x04\xff",
                "length": 16,
                "r": Bitset(0b10011111111, 16)
            },
        ]

        for case in test_list:
            a = case.get("a")
            length = case.get("length", -1)
            if length != -1:
                xbits = Bitset(a, length)
            else:
                xbits = Bitset(a)

            r = case.get("r")
            self.assertEqual(xbits, r)
