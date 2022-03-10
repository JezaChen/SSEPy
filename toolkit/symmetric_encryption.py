# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: symmetric_encryption.py 
@time: 2022/03/09
@contact: jeza@vip.qq.com
@software: PyCharm 
@description: 
"""

import abc
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from toolkit.constants import LENGTH_NOT_LIMIT
from toolkit.symmetric_padding import pkcs7_pad, pkcs7_unpad


class AbstractSymmetricEncryption(metaclass=abc.ABCMeta):
    def __init__(self, *, cipher_length: int, key_length: int, message_length: int):
        self.cipher_length = cipher_length
        self.key_length = key_length
        self.message_length = message_length

    def KeyGen(self) -> bytes:
        pass

    def Encrypt(self, key: bytes, message: bytes) -> bytes:
        pass

    def Decrypt(self, key: bytes, cipher_text: bytes) -> bytes:
        pass


class AESxCBC(AbstractSymmetricEncryption):
    """AES-CBC Schemes, using PKCS7 Padding"""

    def __init__(self, *, key_length=16, cipher_length=LENGTH_NOT_LIMIT, message_length=LENGTH_NOT_LIMIT):
        super(AESxCBC, self).__init__(cipher_length=cipher_length, key_length=key_length, message_length=message_length)
        if key_length not in [16, 24, 32]:
            raise ValueError("The AES key length needs to be 16, 24 or 32 bytes.")
        if cipher_length != LENGTH_NOT_LIMIT and cipher_length % 16:
            raise ValueError("The AES-CBC cipher length needs to be an integer multiple of 16 bytes.")

    def KeyGen(self) -> bytes:
        return os.urandom(self.key_length)

    def Encrypt(self, key: bytes, message: bytes) -> bytes:
        if self.message_length != LENGTH_NOT_LIMIT and len(message) != self.message_length:
            raise ValueError("Message(Input) length mismatch for AES-CBC.")
        if len(key) != self.key_length:
            raise ValueError("Key length mismatch for AES-CBC.")

        # PKCS7 Padding
        padded_message = pkcs7_pad(message, algorithms.AES.block_size)

        iv = os.urandom(algorithms.AES.block_size // 8)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        return iv + encryptor.update(padded_message) + encryptor.finalize()

    def Decrypt(self, key: bytes, cipher_text: bytes) -> bytes:
        if self.cipher_length != LENGTH_NOT_LIMIT and len(cipher_text) != self.cipher_length:
            raise ValueError("Ciphertext length mismatch for AES-CBC.")
        if len(key) != self.key_length:
            raise ValueError("Key length mismatch for AES-CBC.")

        iv, cipher_text = cipher_text[:algorithms.AES.block_size // 8], cipher_text[algorithms.AES.block_size // 8:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(cipher_text) + decryptor.finalize()

        # PKCS7 Unpadding
        output = pkcs7_unpad(padded_plaintext, algorithms.AES.block_size)
        return output
