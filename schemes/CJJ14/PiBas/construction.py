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
@description: ΠBas Construction described by Cash et al. [CJJ+14]
"""
import os

import schemes.interface.inverted_index_sse
from schemes.CJJ14.PiBas.config import DEFAULT_CONFIG, PiBasConfig
from schemes.CJJ14.PiBas.structures import PiBasKey, PiBasToken, PiBasEncryptedDatabase, PiBasResult
from toolkit.bytes_utils import int_to_bytes


class PiBas(schemes.interface.inverted_index_sse.InvertedIndexSSE):
    """PiBas Construction described by Cash et al. [CJJ+14]"""

    def __init__(self, config: dict = DEFAULT_CONFIG):
        super(PiBas, self).__init__()
        self.config = PiBasConfig(config)
        pass

    def _Gen(self) -> PiBasKey:
        """
        Generate Key
        K2 is not used here now.
        """
        K = os.urandom(self.config.param_lambda)
        return PiBasKey(K)

    def _Enc(self, K: PiBasKey, database: dict) -> PiBasEncryptedDatabase:
        """Encrypted the given database under the key"""
        K = K.K
        L = []

        for keyword in database:
            K1 = self.config.prf_f(K, b'\x01' + keyword)
            K2 = self.config.prf_f(K, b'\x02' + keyword)
            for c, identifier in enumerate(database[keyword]):
                l = self.config.prf_f(K1, int_to_bytes(c))
                d = self.config.ske.Encrypt(K2, identifier)
                L.append((l, d))
        return PiBasEncryptedDatabase.build_from_list(L)

    def _Trap(self, K: PiBasKey, keyword: bytes) -> PiBasToken:
        """Trapdoor Generation Algorithm"""
        K = K.K
        K1 = self.config.prf_f(K, b'\x01' + keyword)
        K2 = self.config.prf_f(K, b'\x02' + keyword)
        return PiBasToken(K1, K2)

    def _Search(self, edb: PiBasEncryptedDatabase,
                tk: PiBasToken) -> PiBasResult:
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
            result.append(self.config.ske.Decrypt(K2, cipher))
            c += 1

        return PiBasResult(result)

    def KeyGen(self) -> PiBasKey:
        key = self._Gen()
        return key

    def EDBSetup(self, key: PiBasKey,
                 database: dict) -> PiBasEncryptedDatabase:
        return self._Enc(key, database)

    def TokenGen(self, key: PiBasKey, keyword: bytes) -> PiBasToken:
        return self._Trap(key, keyword)

    def Search(self, edb: PiBasEncryptedDatabase,
               token: PiBasToken) -> PiBasResult:
        return self._Search(edb, token)
