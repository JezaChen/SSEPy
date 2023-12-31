# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: construction.py 
@time: 2022/03/11
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: Scheme 3 Construction (Construction 5.1) described by Asharov et al. [ANSS16]
"""
import copy
import math
import os
import random

import schemes.interface.oop.inverted_index_sse
from schemes.ANSS16.Scheme3.config import DEFAULT_CONFIG, PiConfig
from schemes.ANSS16.Scheme3.structures import PiKey, PiToken, PiEncryptedDatabase, PiResult
from toolkit.bytes_utils import int_to_bytes, split_bytes_given_slice_len, int_from_bytes
from toolkit.database_utils import get_total_size, parse_identifiers_from_block_given_entry_count_in_one_block


class Pi(schemes.interface.oop.inverted_index_sse.InvertedIndexSSE):
    """Scheme3 Construction described by Asharov et al. [ANSS16]"""

    def __init__(self, config: dict = DEFAULT_CONFIG):
        super(Pi, self).__init__()
        self.config = PiConfig(config)
        pass

    def _Gen(self) -> PiKey:
        """
        Generate Key
        K2 is not used here now.
        """
        K = os.urandom(self.config.param_lambda)
        return PiKey(K)

    def _Enc(self, K: PiKey, database: dict) -> PiEncryptedDatabase:
        """Encrypted the given database under the key"""
        K = K.K
        N = get_total_size(database)
        t = math.ceil(math.log2(N))

        padded_database = copy.deepcopy(database)  # need to deep copy!! Otherwise, it will affect the original database

        # If N is not a power of two, we need to pad DB to
        # satisfy this by adding some dummy keyword-identifier pairs.
        while N < 2 ** t:
            random_keyword = os.urandom(32)
            random_id_list_len = random.randint(1, (2 ** t) - N)
            random_id_list = [os.urandom(self.config.param_identifier_size) for _ in range(random_id_list_len)]
            padded_database[random_keyword] = random_id_list

            N += random_id_list_len

        T_list = [[] for _ in range(t + 1)]  # t+1 empty lists T0, T1, ... , Tt
        S = []

        for keyword in padded_database:
            ni = len(padded_database[keyword])
            pi = math.ceil(math.log2(ni))
            # If necessary, pad DB(wi) with dummy identifiers in order to contain exactly 2^{pi} elements.
            padded_database[keyword].extend((os.urandom(self.config.param_identifier_size) for _ in range((2 ** pi) - ni)))

            prf_output = self.config.prf(K, keyword)
            li, Ki, li_prime, Ki_prime = split_bytes_given_slice_len(prf_output, [self.config.param_l,
                                                                                  self.config.param_k,
                                                                                  self.config.param_l_prime,
                                                                                  self.config.param_k_prime])

            cipher_list = [self.config.ske.Encrypt(Ki, identifier) for identifier in padded_database[keyword]]
            di = b"".join(cipher_list)

            # math.ceil(t / 8) --> max_bytes represent |DB(w)|
            ni_prime = self.config.ske.Encrypt(Ki_prime, int_to_bytes(ni, math.ceil(t / 8)))
            T_list[pi].append((li, di))
            S.append((li_prime, ni_prime))

        # padding each list
        for i in range(t + 1):
            d_len = (2 ** i) * len(self.config.ske.Encrypt(b"\x00" * self.config.param_k_prime,
                                                           b"\x00" * self.config.param_identifier_size))
            T_list[i].extend(
                ((os.urandom(self.config.param_l), os.urandom(d_len)) for _ in range((2 ** (t - i)) - len(T_list[i]))))

        # padding list S to N elements
        S.extend(
            ((os.urandom(self.config.param_l_prime), os.urandom(math.ceil(t / 8)))
             for _ in range(N - len(S)))
        )

        # create HT(L0), ..., HT(Lt)
        HT_L_list = []
        for i in range(t + 1):
            HT_L_list.append(PiEncryptedDatabase.create_hash_table(T_list[i]))
        # create HT(S)
        HT_S = PiEncryptedDatabase.create_hash_table(S)

        return PiEncryptedDatabase(HT_S, HT_L_list, self.config)

    def _Trap(self, K: PiKey, keyword: bytes) -> PiToken:
        """Trapdoor Generation Algorithm"""
        K = K.K
        prf_output = self.config.prf(K, keyword)
        li, Ki, li_prime, Ki_prime = split_bytes_given_slice_len(prf_output, [self.config.param_l,
                                                                              self.config.param_k,
                                                                              self.config.param_l_prime,
                                                                              self.config.param_k_prime])
        return PiToken(li, Ki, li_prime, Ki_prime)

    def _Search(self, edb: PiEncryptedDatabase, tk: PiToken) -> PiResult:
        """Search Algorithm"""
        HT_S = edb.HT_S
        HT_L_list = edb.HT_L_list
        li, Ki, li_prime, Ki_prime = tk.li, tk.Ki, tk.li_prime, tk.Ki_prime

        result = []
        ni_prime = HT_S.get(li_prime)
        if ni_prime is None:
            return PiResult(result)

        # the actual size of DB(w)
        ni_bytes = self.config.ske.Decrypt(Ki_prime, ni_prime)
        ni = int_from_bytes(ni_bytes)
        pi = math.ceil(math.log2(ni))
        if pi >= len(HT_L_list):  # size overflow
            return PiResult(result)

        # Obtain the block di
        di = HT_L_list[pi].get(li)
        if di is None:
            return PiResult(result)

        # Parse block di
        cipher_list = parse_identifiers_from_block_given_entry_count_in_one_block(di, 2 ** pi)

        # Decrypt the first ni elements of this block using the key Ki
        result.extend((self.config.ske.Decrypt(Ki, cipher) for cipher in cipher_list[:ni]))

        return PiResult(result)

    def KeyGen(self) -> PiKey:
        key = self._Gen()
        return key

    def EDBSetup(self,
                 key: PiKey,
                 database: dict
                 ) -> PiEncryptedDatabase:
        return self._Enc(key, database)

    def TokenGen(self, key: PiKey, keyword: bytes) -> PiToken:
        return self._Trap(key, keyword)

    def Search(self,
               edb: PiEncryptedDatabase,
               token: PiToken) -> PiResult:
        return self._Search(edb, token)
