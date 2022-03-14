# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: bits.py 
@time: 2022/03/12
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: BitSet Class
"""

import math
from collections.abc import Sequence

from toolkit.bytes_utils import int_from_bytes


class Bitset(Sequence):
    """A very simple bitset implementation for Python.
    Note that, like with normal numbers, the leftmost
    index is the MSB, and like normal sequences, that
    is 0.

    Usage:
        >>> b = Bitset(5)
        >>> b
        Bitset(101)
        >>> b[:]
        [True, False, True]
        >>> b[0] = False
        >>> b
        Bitset(001)
        >>> b << 1
        Bitset(010)
        >>> b >> 1
        Bitset(000)
        >>> b & 1
        Bitset(001)
        >>> b | 2
        Bitset(011)
        >>> b ^ 6
        Bitset(111)
        >>> ~b
        Bitset(110)
    """

    value = 0
    length = 0

    @classmethod
    def from_sequence(cls, seq: Sequence):
        """Iterates over the sequence to produce a new Bitset.
        As in integers, the 0 position represents the LSB.
        """
        n = 0
        for index, value in enumerate(reversed(seq)):
            n += 2 ** index * bool(int(value))
        b = Bitset(n)
        return b

    def __init__(self, value, length=0):
        """Creates a Bitset with the given integer value."""
        if isinstance(value, Bitset):
            value = int(value)
        elif isinstance(value, bytes):
            value = int_from_bytes(value)

        if not isinstance(value, int):
            raise ValueError("The Bitset constructor only supports copyig of BitSet or int.")

        if length and value.bit_length() > length:
            raise ValueError("The bit length of value if larger than given length.")

        self.value = value
        try:
            self.length = length or math.floor(math.log(value, 2)) + 1
        except Exception:
            self.length = 0

    def __and__(self, other):
        b = Bitset(self.value & int(other))
        b.length = max((self.length, other.length))
        return b

    def __or__(self, other):
        b = Bitset(self.value | int(other))
        b.length = max((self.length, other.length))
        return b

    def __invert__(self):
        b = Bitset((~self.value) & ((1 << self.length) - 1))
        b.length = self.length
        return b

    def __xor__(self, value):
        b = Bitset(self.value ^ int(value))
        b.length = max((self.length, value.length))
        return b

    def __lshift__(self, value):
        """Logical left shift, high bits will be lost"""
        b = Bitset(self.value << int(value) & ((1 << self.length) - 1))
        b.length = self.length  # fixed length
        return b

    def __rshift__(self, value):
        b = Bitset(self.value >> int(value))
        b.length = self.length  # fixed length
        return b

    def __eq__(self, other):
        try:
            return self.value == other.value and self.length == other.length
        except Exception:
            return self.value == other

    def __int__(self):
        return self.value

    def __bytes__(self):
        output_length = (self.length + 7) // 8
        return self.value.to_bytes(output_length, byteorder="big")

    def __str__(self):
        s = ""
        for i in self[:]:
            s += "1" if i else "0"
        return s

    def __repr__(self):
        return "Bitset(%s)" % str(self)

    def __getitem__(self, s):
        """Gets the specified position.

        Like normal integers, 0 represents the MSB.
        """
        try:
            start, stop, step = s.indices(len(self))
            results = []
            for position in range(start, stop, step):
                pos = len(self) - position - 1
                results.append(bool(self.value & (1 << pos)))
            return results
        except:
            pos = len(self) - s - 1
            return bool(self.value & (1 << pos))

    def __setitem__(self, s, value):
        """Sets the specified position/s to value.

        Like normal integers, 0 represents the MSB.
        """
        try:
            start, stop, step = s.indices(len(self))
            for position in range(start, stop, step):
                pos = len(self) - position - 1
                if value:
                    self.value |= (1 << pos)
                else:
                    self.value &= ~(1 << pos)
            maximum_position = max((start + 1, stop, len(self)))
            self.length = maximum_position
        except:
            pos = len(self) - s - 1
            if value:
                self.value |= (1 << pos)
            else:
                self.value &= ~(1 << pos)
            if len(self) < pos:
                self.length = pos
        return self

    def __iter__(self):
        """Iterates over the values in the bitset."""
        for i in self[:]:
            yield i

    def __len__(self):
        """Returns the length of the bitset."""
        return self.length

    def concat(self, b):
        if not isinstance(b, Bitset):
            raise ValueError("Only allow concat between Bitset")
        return Bitset((self.value << b.length) + b.value, self.length + b.length)

    def __add__(self, other):
        return self.concat(other)

    def bit_length(self):
        return self.length

    def get_higher_bits(self, bit_len: int):
        if bit_len < 0:
            raise ValueError("The parameter bit_len is less than or equal to 0")

        if bit_len > self.length:
            raise ValueError("The parameter bit_len is greater than the actual length of the bits")

        return Bitset(self >> max(self.length - bit_len, 0), bit_len)

    def get_lower_bits(self, bit_len: int):
        if bit_len < 0:
            raise ValueError("The parameter bit_len is less than or equal to 0")

        if bit_len > self.length:
            raise ValueError("The parameter bit_len is greater than the actual length of the bits")

        return Bitset((self << max(self.length - bit_len, 0)) >> max(self.length - bit_len, 0), bit_len)
