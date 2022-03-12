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
@description:
@note: Here PRP is bitwise PRP
"""
import os

import schemes.interface.inverted_index_sse
from schemes.CGKO06.SSE2.config import DEFAULT_CONFIG, SSE2Config
from schemes.CGKO06.SSE2.structures import SSE2Key, SSE2Token, SSE2EncryptedDatabase, SSE2Result
from toolkit.bits import Bitset
from toolkit.bytes_utils import int_to_bytes


class SSE2(schemes.interface.inverted_index_sse.InvertedIndexSSE):
    """SSE-2 Construction described by Curtomola et al. [CGKO06]"""

    def __init__(self, config: dict = DEFAULT_CONFIG):
        super(SSE2, self).__init__()
        self.config = SSE2Config(config)
        pass

    def _Gen(self) -> SSE2Key:
        """
        Generate Key
        K2 is not used here now.
        """
        key_tuple = tuple(os.urandom(self.config.param_k) for _ in range(2))
        return SSE2Key(*key_tuple)

    def _Enc(self, K: SSE2Key, database: dict) -> SSE2EncryptedDatabase:
        """Encrypted the given database under the key"""
        K1, K2 = K.K1, K.K2
        I = {}

        s_prime = 0  # total_size
        document_count_dict = {}  # the number of entries in I that already contain id(Di)

        for keyword in database:
            s_prime += len(database[keyword])
            for j, identifier in enumerate(database[keyword], start=1):
                I[int(
                    self.config.prp_pi(Bitset(K1,
                                              length=self.config.param_k_bits),
                                       Bitset(keyword, length=self.config.param_l_bits) +
                                       Bitset(int_to_bytes(j, self.config.param_log2_n_plus_max_bytes),
                                              length=self.config.param_log2_n_plus_max),
                                       )
                )] = identifier

                document_count_dict[identifier] = document_count_dict.get(identifier, 0) + 1

        n = self.config.param_n

        if s_prime < self.config.param_s:
            for identifier in document_count_dict:
                for l in range(document_count_dict[identifier] - self.config.param_max):
                    I[int(
                        self.config.prp_pi(Bitset(K1,
                                                  length=self.config.param_k_bits),
                                           Bitset(b"\x00" * self.config.param_l,
                                                  length=self.config.param_l_bits) +
                                           Bitset(int_to_bytes(n + l, self.config.param_log2_n_plus_max_bytes),
                                                  length=self.config.param_log2_n_plus_max)
                                           ))] = identifier
                n += document_count_dict[identifier] - self.config.param_max
        return SSE2EncryptedDatabase(I)

    def _Trap(self, K: SSE2Key, keyword: bytes) -> SSE2Token:
        """Trapdoor Generation Algorithm"""
        K1 = K.K1
        t = []
        for i in range(1, self.config.param_n + 1):
            t.append(int(self.config.prp_pi(Bitset(K1,
                                                   length=self.config.param_k_bits),
                                            Bitset(keyword, length=self.config.param_l_bits) +
                                            Bitset(int_to_bytes(i, self.config.param_log2_n_plus_max_bytes),
                                                   length=self.config.param_log2_n_plus_max))
                         ))
        return SSE2Token(t)

    def _Search(self, edb: SSE2EncryptedDatabase, tk: SSE2Token) -> SSE2Result:
        """Search Algorithm"""
        I = edb.I
        t_list = tk.t
        result = []

        for ti in t_list:
            identifier = I.get(ti)
            if identifier is None:
                break
            result.append(identifier)

        return SSE2Result(result)

    def KeyGen(self) -> SSE2Key:
        key = self._Gen()
        return key

    def EDBSetup(self,
                 key: SSE2Key,
                 database: dict
                 ) -> SSE2EncryptedDatabase:
        return self._Enc(key, database)

    def TokenGen(self, key: SSE2Key, keyword: bytes) -> SSE2Token:
        return self._Trap(key, keyword)

    def Search(self,
               edb: SSE2EncryptedDatabase,
               token: SSE2Token) -> SSE2Result:
        return self._Search(edb, token)
