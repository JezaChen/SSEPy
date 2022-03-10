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
from schemes.CGKO06.SSE1.param import param_k, param_s, ske1, prp_psi, param_log2s, prp_pi, prf_f, \
    param_identifier_size, param_dictionary_size
from schemes.CGKO06.SSE1.structures import SSE1Key, SSE1EncryptedDatabase, SSE1Token, SSE1Result
from toolkit.bytes_utils import int_to_bytes, int_from_bytes, bytes_xor, add_leading_zeros


class SSE1(schemes.interface.inverted_index_sse.InvertedIndexSSE):
    """SSE-1 Construction described by Curtomola et al. [CGKO06]"""

    def __init__(self):
        super(SSE1, self).__init__()
        pass

    def _Gen(self):
        """
        Generate Key
        K4 is not used here now.
        """
        key_tuple = tuple(os.urandom(param_k) for _ in range(4))
        return key_tuple

    def _Enc(self, K: tuple, database: dict):
        """Encrypted the given database under the key"""
        K1, K2, K3, K4 = K

        ctr = 1
        A = [b'\x00'] * param_s
        T = {}

        for keyword in database:
            first_node_addr = None
            # Sample a key Ki,0 <-$- {0, 1}k
            K_i = [os.urandom(param_k)]

            for j, identifier in enumerate(database[keyword], start=1):  # j begins from 1
                if j == len(database[keyword]):  # not process last node here
                    break

                # Generate a key Ki,j ← SKE1.Gen(1^k)
                K_i.append(ske1.KeyGen())

                # Create a node
                N_i_j = identifier + K_i[j] + prp_psi(K1, int_to_bytes(ctr + 1, param_log2s // 8))

                # Encrypt node N_i_j under key Ki,j-1
                addr_in_A = prp_psi(K1, int_to_bytes(ctr, param_log2s // 8))
                A[int_from_bytes(addr_in_A)] = ske1.Encrypt(K_i[j - 1], N_i_j)

                # Record first node address
                if j == 1:
                    first_node_addr = addr_in_A

                ctr += 1

            # For the last node of Li
            last_node = database[keyword][-1] + b"\x00" * param_k + b"\x00" * prp_psi.message_length
            last_node_addr_in_A = prp_psi(K1, int_to_bytes(ctr, param_log2s // 8))
            A[int_from_bytes(last_node_addr_in_A)] = ske1.Encrypt(K_i[-1], last_node)
            if first_node_addr is None:  # only one entry
                first_node_addr = last_node_addr_in_A
            ctr += 1

            # Add item to Look-up Table T
            T[prp_pi(K3, add_leading_zeros(keyword, prp_pi.message_length))] = \
                bytes_xor(first_node_addr + K_i[0], prf_f(K2, add_leading_zeros(keyword, prf_f.message_length)))

        # Fill random values for empty entry in A
        existing_entry_size = len(ske1.Encrypt(b"\x00" * param_k,
                                               b"\x00" * (param_identifier_size + param_k + prp_psi.message_length))
                                  )
        for i in range(len(A)):
            if A[i] == b'\x00':
                A[i] = os.urandom(existing_entry_size)  # the same size as the existing s' entries of A

        # Fill random values to T so that |T| = |∆|
        for _ in range(param_dictionary_size - len(T)):
            T[os.urandom(prp_pi.message_length)] = os.urandom(prf_f.output_length)

        return A, T

    def _Trap(self, K, keyword: bytes):
        """Trapdoor Generation Algorithm"""
        _, K2, K3, *_ = K
        return prp_pi(K3, add_leading_zeros(keyword, prp_pi.message_length)), \
               prf_f(K2, add_leading_zeros(keyword, prf_f.message_length))

    def _Search(self, I: tuple, t: tuple):
        """Search Algorithm"""
        A, T = I  # Parse encrypted index
        gamma, eta = t  # Parse token(trapdoor)
        theta = T.get(gamma)
        if theta is None:
            return None
        xor_result = bytes_xor(theta, eta)  # θ ⊕ η

        # parse θ ⊕ η as α||K', α is the first node address, K' is the key to decrypt
        node_addr, K_prime = xor_result[:prp_psi.message_length], xor_result[prp_psi.message_length:]

        result = []
        while True:
            node_cipher = A[int_from_bytes(node_addr)]
            node = ske1.Decrypt(K_prime, node_cipher)
            # parse the node
            file_identifier, next_key, next_node_addr = node[:param_identifier_size], \
                                                        node[param_identifier_size:param_identifier_size + param_k], \
                                                        node[param_identifier_size + param_k:]

            result.append(file_identifier)
            node_addr, K_prime = next_node_addr, next_key
            if node_addr == b'\x00' * (param_log2s // 8):  # next ptr is null
                break
        return result

    def KeyGen(self) -> SSE1Key:
        original_key = self._Gen()
        return SSE1Key(*original_key)

    def EDBSetup(self,
                 key: SSE1Key,
                 database: dict
                 ) -> SSE1EncryptedDatabase:
        original_key = key.K1, key.K2, key.K3, key.K4
        A, T = self._Enc(original_key, database)
        return SSE1EncryptedDatabase(A, T)

    def TokenGen(self, key: SSE1Key, keyword: bytes) -> SSE1Token:
        original_key = key.K1, key.K2, key.K3, key.K4
        gamma, eta = self._Trap(original_key, keyword)
        return SSE1Token(gamma, eta)

    def Search(self,
               edb: SSE1EncryptedDatabase,
               token: SSE1Token) -> SSE1Result:
        original_token = token.gamma, token.eta
        I = edb.A, edb.T
        result = self._Search(I, original_token)
        return SSE1Result(result)
