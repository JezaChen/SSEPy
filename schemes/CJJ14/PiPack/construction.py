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
@description: ΠBas Construction described by Cash et al. [CJJ+14]
"""
import os

import schemes.interface.inverted_index_sse
from schemes.CJJ14.PiPack.config import DEFAULT_CONFIG, PiPackConfig
from schemes.CJJ14.PiPack.structures import PiPackKey, PiPackToken, PiPackEncryptedDatabase, PiPackResult
from toolkit.bytes_utils import int_to_bytes
from toolkit.database_utils import partition_identifiers_to_blocks, parse_identifiers_from_block


class PiPack(schemes.interface.inverted_index_sse.InvertedIndexSSE):
    """PiPack Construction described by Cash et al. [CJJ+14]"""

    def __init__(self, config: dict = DEFAULT_CONFIG):
        super(PiPack, self).__init__()
        self.config = PiPackConfig(config)
        pass

    def _Gen(self) -> PiPackKey:
        """
        Generate Key
        K2 is not used here now.
        """
        K = os.urandom(self.config.param_lambda)
        return PiPackKey(K)

    def _Enc(self, K: PiPackKey, database: dict) -> PiPackEncryptedDatabase:
        """Encrypted the given database under the key"""
        K = K.K
        L = []

        for keyword in database:
            K1 = self.config.prf_f(K, b'\x01' + keyword)
            K2 = self.config.prf_f(K, b'\x02' + keyword)
            block_list = partition_identifiers_to_blocks(database[keyword],
                                                         self.config.param_B,
                                                         self.config.param_identifier_size)

            for c, block in enumerate(block_list):
                l = self.config.prf_f(K1, int_to_bytes(c))
                d = self.config.ske.Encrypt(K2, block)
                L.append((l, d))
        return PiPackEncryptedDatabase.build_from_list(L)

    def _Trap(self, K: PiPackKey, keyword: bytes) -> PiPackToken:
        """Trapdoor Generation Algorithm"""
        K = K.K
        K1 = self.config.prf_f(K, b'\x01' + keyword)
        K2 = self.config.prf_f(K, b'\x02' + keyword)
        return PiPackToken(K1, K2)

    def _Search(self, edb: PiPackEncryptedDatabase, tk: PiPackToken) -> PiPackResult:
        """Search Algorithm"""
        D = edb.D
        K1, K2 = tk.K1, tk.K2
        result = []
        c = 0
        while True:
            addr = self.config.prf_f(K1, int_to_bytes(c))
            cipher = D.get(addr)
            if cipher is None:
                break
            result.extend(parse_identifiers_from_block(self.config.ske.Decrypt(K2, cipher),
                                                       self.config.param_identifier_size))
            c += 1

        return PiPackResult(result)

    def KeyGen(self) -> PiPackKey:
        key = self._Gen()
        return key

    def EDBSetup(self,
                 key: PiPackKey,
                 database: dict
                 ) -> PiPackEncryptedDatabase:
        return self._Enc(key, database)

    def TokenGen(self, key: PiPackKey, keyword: bytes) -> PiPackToken:
        return self._Trap(key, keyword)

    def Search(self,
               edb: PiPackEncryptedDatabase,
               token: PiPackToken) -> PiPackResult:
        return self._Search(edb, token)
