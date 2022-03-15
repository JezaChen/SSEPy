# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: symmetric_padding.py 
@time: 2022/03/09
@contact: jeza@vip.qq.com
@software: PyCharm 
@description: 
"""

from cryptography.hazmat.primitives import padding


def pkcs7_pad(message: bytes, block_size: int) -> bytes:
    padder = padding.PKCS7(block_size).padder()
    padded_message = padder.update(message)
    padded_message += padder.finalize()
    return padded_message


def pkcs7_unpad(padded_message: bytes, block_size: int) -> bytes:
    unpadder = padding.PKCS7(block_size).unpadder()
    output = unpadder.update(padded_message)
    output += unpadder.finalize()
    return output
