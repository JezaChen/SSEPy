# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: construction.py 
@time: 2022/03/25
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: Π Construction described by Demertzis et al. [DP17]
"""
import math
import os
import random
import typing

import schemes.interface.inverted_index_sse
import toolkit.list_utils
from schemes.DP17.Pi.config import DEFAULT_CONFIG, PiConfig
from schemes.DP17.Pi.structures import PiKey, PiToken, PiEncryptedDatabase, PiResult
from toolkit.bytes_utils import int_to_bytes, bytes_xor, int_from_bytes
from toolkit.database_utils import get_total_size


def _divide_to_buckets(
        array_size: int,
        bucket_size: int) -> (typing.List[int], typing.List[typing.List]):
    """
    Pre-slices the array into buckets based on the size of the array and the size of the buckets,
    returning the number of elements remaining in each bucket
    and the keyword-file identifier pairs contained in each bucket.
    """
    remaining_count_list = [
        min(bucket_size, array_size - begin_index)
        for begin_index in range(0, array_size, bucket_size)
    ]
    w_id_pair_list = [[] for _ in range(len(remaining_count_list))]
    return remaining_count_list, w_id_pair_list


class Pi(schemes.interface.inverted_index_sse.InvertedIndexSSE):
    """Pi Construction described by Demertzis et al. [DP17]"""

    def __init__(self, config: dict = DEFAULT_CONFIG):
        super(Pi, self).__init__()
        self.config = PiConfig(config)
        pass

    def _find_adjacent_i(self, db_w_len: int,
                         levels_list: typing.List[int]) -> int:
        """
        Find adjacent j and i in L such that
        L·2j < |D(w)| ≤ L·2i (if i is the smallest level, we ignore the lower bound).
        :return: only returns i
        """
        lo, hi = 0, len(levels_list)
        while lo <= hi:
            mid = (lo + hi) >> 1
            if self.config.param_L * 2**(levels_list[mid]) >= db_w_len:
                hi = mid - 1
            else:
                lo = mid + 1
        return levels_list[lo]

    def _get_remaining_enough_space_buckets(
            self, chunk_size: int,
            remaining_list: typing.List[int]) -> typing.List[int]:
        """
        returns the set of buckets in Ai that have enough space for chunk c
        :param: chunk_size the size of chunk c
        :param: remaining_list space remaining for each element of the array Ai
        """
        for bucket_index, bucket_remaining in enumerate(remaining_list):
            if bucket_remaining >= chunk_size:
                yield bucket_index

    def _Gen(self) -> PiKey:
        """
        Generate Key
        """
        k1, k2, k3 = (os.urandom(self.config.param_lambda) for _ in range(3))
        return PiKey(k1, k2, k3)

    def _Enc(self, K: PiKey, database: dict) -> PiEncryptedDatabase:
        """Encrypted the given database under the key"""
        k1, k2, k3 = K.k1, K.k2, K.k3
        N = get_total_size(database)
        l = math.ceil(math.log2(N))
        s = math.ceil(l * self.config.param_actual_storage_level_ratio)
        p = math.ceil(l / s)
        levels = [l - i * p for i in range(0, s)]
        if self.config.param_L > 1:
            levels.append(0)
        levels.reverse()

        # Initialize a hash table HT that can store up to N elements.
        HT = {}

        level_to_remaining_count_list_map = {
        }  # level -> remaining count in each bucket
        level_to_w_id_pair_list_map = {
        }  # level -> (w, id) pairs in each bucket

        for i in levels:  # each evenly distributed level i ∈ L
            level_to_remaining_count_list_map[i], level_to_w_id_pair_list_map[
                i] = _divide_to_buckets(2 * N + 2**(i + 1), 2**(i + 1))

        for keyword in database:
            # Find adjacent j and i in L such that L· 2j < |D(w)| ≤ L· 2i
            # (if i is the smallest level, we ignore the lower bound)
            i = self._find_adjacent_i(len(database[keyword]), levels)

            # Split D(w) into a set C_w of chunks containing q_w chunks of size 2i and one chunk of size r_w < 2^i.
            Cw = toolkit.list_utils.chunks(database[keyword], 2**i)
            count = 0
            for c in Cw:
                count += 1
                # A is the set of buckets in Ai that have enough space for chunk
                A = list(
                    self._get_remaining_enough_space_buckets(
                        2**i, level_to_remaining_count_list_map[i]))
                # Pick one bucket a ∈ A (say Ai[x]) uniformly at random
                x = random.choice(A)
                for identifier in c:
                    # store c in a at the first available position.
                    level_to_w_id_pair_list_map[i][x].append(
                        (keyword, identifier))

                    # HT.add(H(Fk1(w)||count), [i||x] ⊕ H(Fk2(w)||count))
                    key = self.config.hash_h(
                        self.config.prf_f(k1, keyword) + int_to_bytes(count))
                    i_concat_x = int_to_bytes(i,
                                              self.config.param_hash_h_digest_size // 2) + \
                        int_to_bytes(x,
                                     self.config.param_hash_h_digest_size -
                                     self.config.param_hash_h_digest_size // 2)
                    HT[key] = bytes_xor(
                        i_concat_x,
                        self.config.hash_h(
                            self.config.prf_f(k2, keyword) +
                            int_to_bytes(count)))
                level_to_remaining_count_list_map[i][x] -= len(c)

        # Add random (key, value) pairs to HT so that the total number of elements it stores is N.
        for _ in range(N - len(HT)):
            HT[os.urandom(self.config.param_hash_h_digest_size)] = os.urandom(
                self.config.param_hash_h_digest_size)

        A_dict = {}
        for i in levels:
            Ai = []
            for bucket_index, w_id_pair_list in enumerate(
                    level_to_w_id_pair_list_map[i]):
                for _ in range(
                        level_to_remaining_count_list_map[i][bucket_index]):
                    w_id_pair_list.append((None, None))

                # Randomly permute all entries (w, id) within b
                random.shuffle(w_id_pair_list)
                cipher_list = []
                # Replace each entry (w, id) of b with RND.Enckey(id||0λ) where key = Fk3 (w).
                for keyword, identifier in w_id_pair_list:
                    if keyword is None and identifier is None:
                        cipher_list.append(
                            os.urandom(
                                self.config.param_identifier_cipher_len))
                    else:
                        cipher_list.append(
                            self.config.rnd.Encrypt(
                                self.config.prf_f(k3, keyword), identifier +
                                b"\x00" * self.config.param_lambda))
                chunk_bytes = b"".join(cipher_list)
                Ai.append(chunk_bytes)
            A_dict[i] = Ai

        return PiEncryptedDatabase(HT, A_dict)

    def _Trap(self, K: PiKey, keyword: bytes) -> PiToken:
        """Trapdoor Generation Algorithm"""
        k1, k2, k3 = K.k1, K.k2, K.k3
        # tag ← F(k1, w), vtag ← F(k2, w), etag ← F(k3, w)
        tag = self.config.prf_f(k1, keyword)
        vtag = self.config.prf_f(k2, keyword)
        etag = self.config.prf_f(k3, keyword)
        return PiToken(tag, vtag, etag)

    def _Search(self, edb: PiEncryptedDatabase, tk: PiToken) -> PiResult:
        """Search Algorithm"""
        HT, A_dict = edb.HT, edb.A_dict
        tag, vtag, etag = tk.tag, tk.vtag, tk.etag
        result = set()

        for count in range(1,
                           self.config.param_L + 1):  # for count = 1 to L do
            # evalue ← HT.get(H(tag||count))
            evalue = HT.get(self.config.hash_h(tag + int_to_bytes(count)))
            if evalue is not None:
                # [i, offset] ← evalue ⊕ H(vtag||count)
                i_concat_offset = bytes_xor(
                    evalue, self.config.hash_h(vtag + int_to_bytes(count)))
                i_bytes, offset_bytes = i_concat_offset[:self.config.param_hash_h_digest_size // 2], \
                    i_concat_offset[self.config.param_hash_h_digest_size // 2:]

                i = int_from_bytes(i_bytes)
                offset = int_from_bytes(offset_bytes)

                for e in toolkit.list_utils.chunks(
                        A_dict[i][offset],
                        self.config.param_identifier_cipher_len):
                    try:
                        plaintext = self.config.rnd.Decrypt(etag, e)
                        if plaintext[
                                -self.config.
                                param_lambda:] == b"\x00" * self.config.param_lambda:
                            identifier = plaintext[:-self.config.param_lambda]
                            result.add(identifier)
                    except ValueError:
                        continue

        return PiResult(result)

    def KeyGen(self) -> PiKey:
        key = self._Gen()
        return key

    def EDBSetup(self, key: PiKey, database: dict) -> PiEncryptedDatabase:
        return self._Enc(key, database)

    def TokenGen(self, key: PiKey, keyword: bytes) -> PiToken:
        return self._Trap(key, keyword)

    def Search(self, edb: PiEncryptedDatabase, token: PiToken) -> PiResult:
        return self._Search(edb, token)
