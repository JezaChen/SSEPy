# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: construction.py 
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: SSE-1 Construction described by Curtomola et al. [CGKO06]

@paper: Searchable symmetric encryption: improved definitions and efficient constructions
@paper_author: Curtomola et al.
"""
import os

import schemes.interface.inverted_index_sse
from schemes.CGKO06.SSE1.config import DEFAULT_CONFIG, SSE1Config
from schemes.CGKO06.SSE1.structures import SSE1Key, SSE1EncryptedDatabase, SSE1Token, SSE1Result
from toolkit.bits import Bitset
from toolkit.bytes_utils import int_from_bytes, bytes_xor, add_leading_zeros


class SSE1(schemes.interface.inverted_index_sse.InvertedIndexSSE):
    """SSE-1 Construction described by Curtomola et al. [CGKO06]"""

    def __init__(self, config: dict = DEFAULT_CONFIG):
        super(SSE1, self).__init__()
        self.config = SSE1Config(config)
        pass

    def _Gen(self) -> SSE1Key:
        """
        Generate Key
        K4 is not used here now.
        """
        key_tuple = tuple(os.urandom(self.config.param_k) for _ in range(4))
        return SSE1Key(*key_tuple)

    def _Enc(self, K: SSE1Key, database: dict) -> SSE1EncryptedDatabase:
        """Encrypted the given database under the key"""
        K1, K2, K3, K4 = K.K1, K.K2, K.K3, K.K4

        ctr = 1
        A = [b'\x00'] * self.config.param_s
        T = {}

        for keyword in database:
            first_node_addr = None
            # Sample a key Ki,0 <-$- {0, 1}k
            K_i = [os.urandom(self.config.param_k)]

            for j, identifier in enumerate(database[keyword], start=1):  # j begins from 1
                if j == len(database[keyword]):  # not process last node here
                    break

                # Generate a key Ki,j ← SKE1.Gen(1^k)
                K_i.append(self.config.ske1.KeyGen())

                # Create a node
                N_i_j = identifier + K_i[j] + bytes(self.config.prp_psi(
                    Bitset(K1, length=self.config.param_k_bits),
                    Bitset(ctr + 1, length=self.config.param_log2_s)
                ))

                # Encrypt node N_i_j under key Ki,j-1
                addr_in_A = self.config.prp_psi(Bitset(K1, length=self.config.param_k_bits),
                                                Bitset(ctr, length=self.config.param_log2_s))
                A[int(addr_in_A)] = self.config.ske1.Encrypt(K_i[j - 1], N_i_j)

                # Record first node address
                if j == 1:
                    first_node_addr = addr_in_A

                ctr += 1

            # For the last node of Li
            last_node = database[keyword][
                            -1] + b"\x00" * self.config.param_k + b"\x00" * self.config.param_log2_s_bytes
            last_node_addr_in_A = self.config.prp_psi(Bitset(K1, length=self.config.param_k_bits),
                                                      Bitset(ctr, length=self.config.param_log2_s))
            A[int(last_node_addr_in_A)] = self.config.ske1.Encrypt(K_i[-1], last_node)
            if first_node_addr is None:  # only one entry
                first_node_addr = last_node_addr_in_A
            ctr += 1

            # Add item to Look-up Table T
            T[bytes(self.config.prp_pi(Bitset(K3, length=self.config.param_k_bits),
                                       Bitset(keyword, length=self.config.param_l_bits)))] = \
                bytes_xor(bytes(first_node_addr) + K_i[0],
                          self.config.prf_f(K2, add_leading_zeros(keyword, self.config.param_l)))

        # Fill random values for empty entry in A
        existing_entry_size = len(self.config.ske1.Encrypt(b"\x00" * self.config.param_k,
                                                           b"\x00" * (self.config.param_identifier_size +
                                                                      self.config.param_k +
                                                                      self.config.param_log2_s_bytes))
                                  )

        for i in range(len(A)):
            if A[i] == b'\x00':
                A[i] = os.urandom(existing_entry_size)  # the same size as the existing s' entries of A

                # Fill random values to T so that |T| = |∆|
                for _ in range(self.config.param_dictionary_size - len(T)):
                    T[os.urandom(self.config.param_l)] = os.urandom(self.config.prf_f.output_length)

        return SSE1EncryptedDatabase(A, T)

    def _Trap(self, K: SSE1Key, keyword: bytes) -> SSE1Token:
        """Trapdoor Generation Algorithm"""
        K2, K3 = K.K2, K.K3
        return SSE1Token(bytes(self.config.prp_pi(Bitset(K3, length=self.config.param_k_bits),
                                                  Bitset(keyword, length=self.config.param_l_bits))),
                         self.config.prf_f(K2, add_leading_zeros(keyword, self.config.param_l)))

    def _Search(self, I: SSE1EncryptedDatabase, t: SSE1Token) -> SSE1Result:
        """Search Algorithm"""
        A, T = I.A, I.T  # Parse encrypted index
        gamma, eta = t.gamma, t.eta  # Parse token(trapdoor)
        theta = T.get(gamma)
        if theta is None:
            return SSE1Result([])
        xor_result = bytes_xor(theta, eta)  # θ ⊕ η

        # parse θ ⊕ η as α||K', α is the first node address, K' is the key to decrypt
        node_addr, K_prime = xor_result[:self.config.param_log2_s_bytes], xor_result[
                                                                          self.config.param_log2_s_bytes:]

        result = []
        while True:
            node_cipher = A[int_from_bytes(node_addr)]
            node = self.config.ske1.Decrypt(K_prime, node_cipher)
            # parse the node
            file_identifier, next_key, next_node_addr = node[:self.config.param_identifier_size], \
                                                        node[
                                                        self.config.param_identifier_size:self.config.param_identifier_size + self.config.param_k], \
                                                        node[self.config.param_identifier_size + self.config.param_k:]

            result.append(file_identifier)
            node_addr, K_prime = next_node_addr, next_key
            if node_addr == b'\x00' * self.config.param_log2_s_bytes:  # next ptr is null
                break
        return SSE1Result(result)

    def KeyGen(self) -> SSE1Key:
        key = self._Gen()
        return key

    def EDBSetup(self,
                 key: SSE1Key,
                 database: dict
                 ) -> SSE1EncryptedDatabase:
        return self._Enc(key, database)

    def TokenGen(self, key: SSE1Key, keyword: bytes) -> SSE1Token:
        return self._Trap(key, keyword)

    def Search(self,
               edb: SSE1EncryptedDatabase,
               token: SSE1Token) -> SSE1Result:
        return self._Search(edb, token)
