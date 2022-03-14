# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: construction.py 
@time: 2022/03/11
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: Π Construction described by Cash et al. [CT14]
"""
import math
import os
import random

import schemes.interface.inverted_index_sse
from schemes.CT14.Pi.config import DEFAULT_CONFIG, PiConfig
from schemes.CT14.Pi.structures import PiKey, PiToken, PiEncryptedDatabase, PiResult
from toolkit.bytes_utils import int_to_bytes
from toolkit.database_utils import get_total_size, parse_identifiers_from_block_given_entry_count_in_one_block


class Pi(schemes.interface.inverted_index_sse.InvertedIndexSSE):
    """Pi Construction described by Cash et al. [CJJ+14]"""

    def __init__(self, config: dict = DEFAULT_CONFIG):
        super(Pi, self).__init__()
        self.config = PiConfig(config)
        pass

    def _Gen(self) -> PiKey:
        """
        Generate Key
        K2 is not used here now.
        """
        K = os.urandom(self.config.param_k)
        return PiKey(K)

    def _Enc(self, K: PiKey, database: dict) -> PiEncryptedDatabase:
        """Encrypted the given database under the key"""
        K = K.K
        N = get_total_size(database)
        t = math.ceil(math.log2(N))

        # If N is not a power of two, we need to pad DB to
        # satisfy this by adding some dummy keyword-identifier pairs.
        while N < 2 ** t:
            random_keyword = os.urandom(32)
            random_id_list_len = random.randint(1, (2 ** t) - N)
            random_id_list = [os.urandom(self.config.param_identifier_size) for _ in range(random_id_list_len)]
            database[random_keyword] = random_id_list

            N += random_id_list_len

        L_list = [[] for _ in range(t)]  # t empty lists L0, L1, ... , Lt−1

        for keyword in database:
            Kw0_concat_Kw1 = self.config.prf_f(K, keyword)
            Kw0, Kw1 = Kw0_concat_Kw1[:self.config.param_k], Kw0_concat_Kw1[self.config.param_k:]

            c = 0
            for j in range(int(math.log2(len(database[keyword]))), -1, -1):
                if 2 ** j > len(database[keyword]) - c:
                    continue
                cipher_list = [self.config.ske.Encrypt(Kw1, database[keyword][i]) for i in
                               range(c, c + 2 ** j)]
                d = b''.join(cipher_list)
                l = self.config.prf_f_prime(Kw0, int_to_bytes(j))
                L_list[j].append((l, d))
                c += 2 ** j

        # padding each list
        for i in range(t):
            d_len = (2 ** i) * len(self.config.ske.Encrypt(b"\x00" * self.config.param_k_prime,
                                                           b"\x00" * self.config.param_identifier_size))
            L_list[i].extend(
                ((os.urandom(self.config.param_l), os.urandom(d_len)) for _ in range((2 ** (t - i)) - len(L_list[i]))))
        # create HT_0, ..., HT_{t-1}
        HT_list = []
        for i in range(t):
            HT_list.append(PiEncryptedDatabase.create_hash_table(L_list[i]))

        return PiEncryptedDatabase(HT_list, self.config)

    def _Trap(self, K: PiKey, keyword: bytes) -> PiToken:
        """Trapdoor Generation Algorithm"""
        K = K.K
        K0_concat_K1 = self.config.prf_f(K, keyword)
        K0, K1 = K0_concat_K1[:self.config.param_k], K0_concat_K1[self.config.param_k:]
        return PiToken(K0, K1)

    def _Search(self, edb: PiEncryptedDatabase, tk: PiToken) -> PiResult:
        """Search Algorithm"""
        HT_list = edb.HT_list
        t = len(HT_list)
        K0, K1 = tk.K0, tk.K1
        result = []
        for i in range(t - 1, -1, -1):
            l = self.config.prf_f_prime(K0, int_to_bytes(i))
            d = HT_list[i].get(l)
            if d is not None:
                cipher_list = parse_identifiers_from_block_given_entry_count_in_one_block(d, 2 ** i)
                result.extend((self.config.ske.Decrypt(K1, cipher) for cipher in cipher_list))

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
