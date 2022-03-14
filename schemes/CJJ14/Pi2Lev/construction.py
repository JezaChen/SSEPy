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
@description: ΠLev Construction described by Cash et al. [CJJ+14]

@note:
Here, we define the file identifier to start from 1, and the index amount of A to start from 1,
to eliminate the misunderstanding of the de-padding algorithm due to the misunderstanding of 0 as the padding value
"""
import math
import os
import random

import schemes.interface.inverted_index_sse
from schemes.CJJ14.Pi2Lev.config import DEFAULT_CONFIG, Pi2LevConfig, LEVEL_POINTER_OF_ARRAY, LEVEL_FILE_IDENTIFIER
from schemes.CJJ14.Pi2Lev.structures import Pi2LevKey, Pi2LevToken, Pi2LevEncryptedDatabase, Pi2LevResult
from toolkit.bytes_utils import int_to_bytes, int_from_bytes
from toolkit.database_utils import partition_identifiers_to_blocks, \
    parse_identifiers_from_block_given_entry_count_in_one_block


class Pi2Lev(schemes.interface.inverted_index_sse.InvertedIndexSSE):
    """Pi2Lev Construction described by Cash et al. [CJJ+14]"""

    def __init__(self, config: dict = DEFAULT_CONFIG):
        super(Pi2Lev, self).__init__()
        self.config = Pi2LevConfig(config)
        pass

    def _Gen(self) -> Pi2LevKey:
        """
        Generate Key
        K2 is not used here now.
        """
        K = os.urandom(self.config.param_lambda)
        return Pi2LevKey(K)

    def _Enc(self, K: Pi2LevKey, database: dict) -> Pi2LevEncryptedDatabase:
        """Encrypted the given database under the key"""
        K = K.K
        L = []

        dict_block_size = self.config.param_b * self.config.param_identifier_size
        array_block_size = self.config.param_B * self.config.param_identifier_size

        index_size_in_A = self.config.param_index_size_of_A  # Fixed size of the index of A
        A_len = 1
        # calculate the size of A
        for keyword in database:
            if len(database[keyword]) > self.config.param_b:
                A_len += math.ceil(len(database[keyword]) / self.config.param_B)
            if len(database[keyword]) > self.config.param_b_prime * self.config.param_B:
                A_len += math.ceil(len(database[keyword]) / (self.config.param_B * self.config.param_B_prime))

        # verify the size of the index of A is correct
        if A_len > 2 ** (index_size_in_A * 8):
            raise ValueError("Initialization failed, "
                             "please make sure the parameters param_b_prime and param_B_prime are set correctly")

        A = [None] * A_len
        available_pos_list = random.sample(range(1, A_len), A_len - 1)  # index of A start at 1 !!

        for keyword in database:
            K1 = self.config.prf_f(K, b'\x01' + keyword)
            K2 = self.config.prf_f(K, b'\x02' + keyword)

            if len(database[keyword]) <= self.config.param_b:  # DB(w) is small
                db_w_bytes = b''.join(database[keyword])
                # Pad DB(w) to b elements
                db_w_bytes += b'\x00' * (dict_block_size - len(db_w_bytes))
                l = self.config.prf_f(K1, b"\x00")
                d = self.config.ske.Encrypt(K2, LEVEL_FILE_IDENTIFIER + db_w_bytes)
                L.append((l, d))

            elif self.config.param_b < len(database[keyword]) <= self.config.param_B * self.config.param_b_prime:
                # DB(w) is medium
                # Divide identifiers into blocks, encrypt, and store them array A:
                file_id_block_list = partition_identifiers_to_blocks(database[keyword],
                                                                     self.config.param_B,
                                                                     self.config.param_identifier_size,
                                                                     block_size_bytes=array_block_size)

                index_list_in_A = []

                for j, file_id_block in enumerate(file_id_block_list):
                    # store id blocks in array A
                    index_in_A = available_pos_list.pop()  # Choose random empty index
                    index_list_in_A.append(int_to_bytes(index_in_A, output_len=index_size_in_A))

                    d = self.config.ske.Encrypt(K2, LEVEL_FILE_IDENTIFIER + file_id_block)
                    A[index_in_A] = d

                # Encrypt and store a single block of pointers in dictionary D:

                index_of_A_block_bytes = b''.join(index_list_in_A)
                # Pad {i_1, ..., i_t} to b elements if necessary
                index_of_A_block_bytes += b'\x00' * (dict_block_size - len(index_of_A_block_bytes))
                l = self.config.prf_f(K1, b"\x00")
                d = self.config.ske.Encrypt(K2, LEVEL_POINTER_OF_ARRAY + index_of_A_block_bytes)
                L.append((l, d))

            elif self.config.param_B * self.config.param_b_prime < len(database[keyword]) < (
                    self.config.param_B * self.config.param_B_prime) * self.config.param_b_prime:

                # Divide identifiers into blocks, encrypt, and store them array A:

                file_id_block_list = partition_identifiers_to_blocks(database[keyword],
                                                                     self.config.param_B,
                                                                     self.config.param_identifier_size,
                                                                     block_size_bytes=array_block_size)

                first_level_index_list_in_A = []

                for j, file_id_block in enumerate(file_id_block_list):
                    # store id blocks in array A

                    index_in_A = available_pos_list.pop()  # Choose random empty index
                    first_level_index_list_in_A.append(int_to_bytes(index_in_A, output_len=index_size_in_A))

                    d = self.config.ske.Encrypt(K2, LEVEL_FILE_IDENTIFIER + file_id_block)
                    A[index_in_A] = d

                # Divide pointers into blocks, encrypt, and store them array A:

                first_level_index_block_list = partition_identifiers_to_blocks(first_level_index_list_in_A,
                                                                               self.config.param_B_prime,
                                                                               index_size_in_A,
                                                                               block_size_bytes=array_block_size)

                second_level_index_list_in_A = []

                for j, first_index_id_block in enumerate(first_level_index_block_list):
                    # store first level index blocks in array A

                    index_in_A = available_pos_list.pop()  # Choose random empty index
                    second_level_index_list_in_A.append(int_to_bytes(index_in_A, output_len=index_size_in_A))

                    d = self.config.ske.Encrypt(K2, LEVEL_POINTER_OF_ARRAY + first_index_id_block)
                    A[index_in_A] = d

                # Encrypt and store a single block of second-level pointers in dictionary D:

                second_index_of_A_block_bytes = b''.join(second_level_index_list_in_A)
                # Pad {i'_1, ..., i'_t} to b elements if necessary
                second_index_of_A_block_bytes += b'\x00' * (dict_block_size - len(second_index_of_A_block_bytes))
                l = self.config.prf_f(K1, b"\x00")
                d = self.config.ske.Encrypt(K2, LEVEL_POINTER_OF_ARRAY + second_index_of_A_block_bytes)
                L.append((l, d))
            else:
                raise ValueError("DB(w) is too large!")

        D = Pi2LevEncryptedDatabase.create_dictionary_from_list(L)
        return Pi2LevEncryptedDatabase(D, A)

    def _Trap(self, K: Pi2LevKey, keyword: bytes) -> Pi2LevToken:
        """Trapdoor Generation Algorithm"""
        K = K.K
        K1 = self.config.prf_f(K, b'\x01' + keyword)
        K2 = self.config.prf_f(K, b'\x02' + keyword)
        return Pi2LevToken(K1, K2)

    def _Search(self, edb: Pi2LevEncryptedDatabase, tk: Pi2LevToken) -> Pi2LevResult:
        """Search Algorithm"""
        D = edb.D
        A = edb.A
        K1, K2 = tk.K1, tk.K2

        prev_level_result = [self.config.prf_f(K1, b'\x00')]  # from top level to search
        curr_level_result = []
        curr_process_level = 0
        is_in_file_id_level = False

        # prime suffix --> for storing pointers
        param_by_level = [
            ["param_b", "param_b_prime"],  # top-level
            ["param_B", "param_B_prime"],
            ["param_B", "param_B_prime"],
        ]

        while not is_in_file_id_level:
            curr_level_result = []
            if curr_process_level == 0:
                block_cipher_list = (D[block_addr]
                                     for block_addr in prev_level_result)
            else:
                block_cipher_list = (A[int_from_bytes(block_addr)]
                                     for block_addr in prev_level_result)

            block_plaintext_list = [self.config.ske.Decrypt(K2, block_cipher)
                                    for block_cipher in block_cipher_list]
            level_mark = block_plaintext_list[0][:1]
            is_in_file_id_level = (level_mark == LEVEL_FILE_IDENTIFIER)

            # get the parameter representing entry num in one block
            param_key_entry_num_in_one_block = param_by_level[curr_process_level][
                level_mark == LEVEL_POINTER_OF_ARRAY]
            param_val_entry_num_in_one_block = self.config[param_key_entry_num_in_one_block]

            for block_plaintext in block_plaintext_list:
                block_content = block_plaintext[1:]

                curr_level_result.extend(
                    parse_identifiers_from_block_given_entry_count_in_one_block(block_content,
                                                                                param_val_entry_num_in_one_block))

            curr_process_level += 1
            prev_level_result = curr_level_result

        return Pi2LevResult(curr_level_result)

    def KeyGen(self) -> Pi2LevKey:
        key = self._Gen()
        return key

    def EDBSetup(self,
                 key: Pi2LevKey,
                 database: dict
                 ) -> Pi2LevEncryptedDatabase:
        return self._Enc(key, database)

    def TokenGen(self, key: Pi2LevKey, keyword: bytes) -> Pi2LevToken:
        return self._Trap(key, keyword)

    def Search(self,
               edb: Pi2LevEncryptedDatabase,
               token: Pi2LevToken) -> Pi2LevResult:
        return self._Search(edb, token)
