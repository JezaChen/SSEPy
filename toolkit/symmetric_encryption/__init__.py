# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: __init__.py.py 
@time: 2022/03/10
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
__builtin_constructor_cache = {}


def get_symmetric_encryption_implementation(se_name: str):
    cache = __builtin_constructor_cache
    se = cache.get(se_name.lower())
    if se is not None:
        return se

    try:
        if se_name.lower() in {'aes-cbc', 'aes_cbc', 'aescbc'}:
            from .aes import AESxCBC
            cache['aes-cbc'] = cache['aes_cbc'] = cache['aescbc'] = AESxCBC
    except ImportError:
        pass  # no extension module, this hash is unsupported.

    se = cache.get(se_name.lower())
    if se is not None:
        return se

    raise ValueError('unsupported symmetric encryption type ' + se_name)
