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
@description: ΠPtr Construction described by Cash et al. [CJJ+14]

@note:
Here, we define the file identifier to start from 1, and the index amount of A to start from 1,
to eliminate the misunderstanding of the de-padding algorithm due to the misunderstanding of 0 as the padding value
"""
import math
import os
import random

import schemes.interface.inverted_index_sse
from schemes.CJJ14.PiPtr.config import DEFAULT_CONFIG, PiPtrConfig
from schemes.CJJ14.PiPtr.structures import PiPtrKey, PiPtrToken, PiPtrEncryptedDatabase, PiPtrResult
from toolkit.bytes_utils import int_to_bytes, int_from_bytes
from toolkit.database_utils import partition_identifiers_to_blocks, parse_identifiers_from_block_given_entry_count_in_one_block, \
    parse_identifiers_from_block_given_identifier_size


class PiPtr(schemes.interface.inverted_index_sse.InvertedIndexSSE):
    """PiPtr Construction described by Cash et al. [CJJ+14]"""

    def __init__(self, config: dict = DEFAULT_CONFIG):
        super(PiPtr, self).__init__()
        self.config = PiPtrConfig(config)
        pass

    def _Gen(self) -> PiPtrKey:
        """
        Generate Key
        K2 is not used here now.
        """
        K = os.urandom(self.config.param_lambda)
        return PiPtrKey(K)

    def _Enc(self, K: PiPtrKey, database: dict) -> PiPtrEncryptedDatabase:
        """Encrypted the given database under the key"""
        K = K.K
        L = []
        A_len = sum(math.ceil(len(database[keyword]) / self.config.param_B) for keyword in database) + 1
        A = [None] * A_len
        index_size_in_A = math.ceil(math.log2(A_len) / 8)  # Fixed size of the index of A
        available_pos_list = random.sample(range(1, A_len), A_len - 1)  # index of A start at 1 !!

        for keyword in database:
            K1 = self.config.prf_f(K, b'\x01' + keyword)
            K2 = self.config.prf_f(K, b'\x02' + keyword)
            file_id_block_list = partition_identifiers_to_blocks(database[keyword], self.config.param_B,
                                                                 self.config.param_identifier_size)
            index_list_in_A = []

            for j, file_id_block in enumerate(file_id_block_list):
                # store id blocks in array A

                index_in_A = available_pos_list.pop()  # Choose random empty index
                index_list_in_A.append(int_to_bytes(index_in_A, output_len=index_size_in_A))

                d = self.config.ske.Encrypt(K2, file_id_block)
                A[index_in_A] = d

            # partition indices
            index_block_list = partition_identifiers_to_blocks(index_list_in_A, self.config.param_b, index_size_in_A)
            for c, index_block in enumerate(index_block_list):
                l = self.config.prf_f(K1, int_to_bytes(c))
                d_prime = self.config.ske.Encrypt(K2, index_block)
                L.append((l, d_prime))

        D = PiPtrEncryptedDatabase.create_dictionary_from_list(L)
        return PiPtrEncryptedDatabase(D, A)

    def _Trap(self, K: PiPtrKey, keyword: bytes) -> PiPtrToken:
        """Trapdoor Generation Algorithm"""
        K = K.K
        K1 = self.config.prf_f(K, b'\x01' + keyword)
        K2 = self.config.prf_f(K, b'\x02' + keyword)
        return PiPtrToken(K1, K2)

    def _Search(self, edb: PiPtrEncryptedDatabase, tk: PiPtrToken) -> PiPtrResult:
        """Search Algorithm"""
        D = edb.D
        A = edb.A
        K1, K2 = tk.K1, tk.K2
        index_list = []
        result = []

        c = 0
        while True:
            addr = self.config.prf_f(K1, int_to_bytes(c))
            index_block_cipher = D.get(addr)
            if index_block_cipher is None:
                break
            index_list.extend(
                parse_identifiers_from_block_given_entry_count_in_one_block(
                    self.config.ske.Decrypt(K2, index_block_cipher), self.config.param_b))
            c += 1

        for index_in_A in index_list:
            file_id_block_cipher = A[int_from_bytes(index_in_A)]  # need to convert bytes to int
            file_id_block = self.config.ske.Decrypt(K2, file_id_block_cipher)
            result.extend(parse_identifiers_from_block_given_identifier_size(file_id_block,
                                                                             self.config.param_identifier_size))
            pass

        return PiPtrResult(result)

    def KeyGen(self) -> PiPtrKey:
        key = self._Gen()
        return key

    def EDBSetup(self,
                 key: PiPtrKey,
                 database: dict
                 ) -> PiPtrEncryptedDatabase:
        return self._Enc(key, database)

    def TokenGen(self, key: PiPtrKey, keyword: bytes) -> PiPtrToken:
        return self._Trap(key, keyword)

    def Search(self,
               edb: PiPtrEncryptedDatabase,
               token: PiPtrToken) -> PiPtrResult:
        return self._Search(edb, token)
