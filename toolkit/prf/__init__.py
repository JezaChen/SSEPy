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
@description: Pseudorandom Function Implementation
@chinese_description: 伪随机函数实现
"""
__builtin_constructor_cache = {}


def get_prf_implementation(prf_name: str):
    cache = __builtin_constructor_cache
    prf = cache.get(prf_name.lower())
    if prf is not None:
        return prf

    try:
        if prf_name.lower() in {'hmacprf', 'hmac-prf', 'hmac_prf'}:
            from toolkit.prf.hmac_prf import HmacPRF
            cache['hmacprf'] = cache['hmac-prf'] = cache['hmac_prf'] = HmacPRF
    except ImportError:
        pass  # no extension module, this hash is unsupported.

    prf = cache.get(prf_name.lower())
    if prf is not None:
        return prf

    raise ValueError('unsupported PRF type ' + prf_name)
