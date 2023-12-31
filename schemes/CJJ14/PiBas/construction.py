# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: construction.py 
@time: 2023/12/30
@contact: jeza@vip.qq.com
@site:
@software: PyCharm
@description: ΠBas Construction described by Cash et al. [CJJ+14]
"""
import os

import schemes.interface.functional.inverted_index_sse
from schemes.CJJ14.PiBas.config import PiBasConfig
from schemes.CJJ14.PiBas.structures import PiBasKey, PiBasToken, PiBasEncryptedDatabase, PiBasResult
from schemes.interface.functional.function_marker import SSEFunctions
from toolkit.bytes_utils import int_to_bytes


def PiBas_construction(config: PiBasConfig):
    # === Params ===
    # λ: security parameter
    lambda_ = config.param_lambda
    # PRF: Pseudorandom Function
    # PRF_f: Pseudorandom Function f
    PRF_f = config.prf_f
    # SKE: Symmetric Key Encryption
    SKE = config.ske

    # === Functions ===
    @SSEFunctions.KeyGen
    def Gen() -> PiBasKey:
        """
        Generate Key
        K2 is not used here now.
        """
        K = os.urandom(lambda_)
        return PiBasKey(K)

    @SSEFunctions.EDBSetup
    def Enc(K: PiBasKey, database: dict) -> PiBasEncryptedDatabase:
        """Encrypted the given database under the key"""
        K = K.K
        L = []

        for keyword in database:
            K1 = PRF_f(K, b'\x01' + keyword)
            K2 = PRF_f(K, b'\x02' + keyword)
            for c, identifier in enumerate(database[keyword]):
                l = PRF_f(K1, int_to_bytes(c))
                d = SKE.Encrypt(K2, identifier)
                L.append((l, d))
        return PiBasEncryptedDatabase.build_from_list(L)

    @SSEFunctions.TokenGen
    def Trap(K: PiBasKey, keyword: bytes) -> PiBasToken:
        """Trapdoor Generation Algorithm"""
        K = K.K
        K1 = PRF_f(K, b'\x01' + keyword)
        K2 = PRF_f(K, b'\x02' + keyword)
        return PiBasToken(K1, K2)

    @SSEFunctions.Search
    def Search(edb: PiBasEncryptedDatabase, tk: PiBasToken) -> PiBasResult:
        """Search Algorithm"""
        D = edb.D
        K1, K2 = tk
        result = []
        c = 0
        while True:
            addr = PRF_f(K1, int_to_bytes(c))
            cipher = D.get(addr)
            if cipher is None:
                break
            result.append(SKE.Decrypt(K2, cipher))
            c += 1

        return PiBasResult(result)

    return Gen, Enc, Trap, Search


class PiBas(schemes.interface.functional.inverted_index_sse.InvertedIndexSSE):
    """PiBas Construction described by Cash et al. [CJJ+14]"""
    _constructor = PiBas_construction
    _config_class = PiBasConfig

