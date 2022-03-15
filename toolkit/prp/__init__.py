# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: __init__.py.py 
@time: 2022/03/10
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: Pseudorandom Permutation Implementation
@chinese_description: 伪随机置换实现
"""

__builtin_constructor_cache = {}


def get_prp_implementation(prp_name: str):
    cache = __builtin_constructor_cache
    prp = cache.get(prp_name.lower())
    if prp is not None:
        return prp

    try:
        if prp_name.lower() in {'lubyrackoffprp', 'luby-rackoff-prp', 'luby_rackoff_prp'}:
            from .luby_rackoff_prp import LubyRackoffPRP
            cache['lubyrackoffprp'] = cache['luby-rackoff-prp'] = cache['luby_rackoff_prp'] = LubyRackoffPRP
        elif prp_name.lower() in {'hmaclubyrackoffprp', 'hmac-luby-rackoff-prp', 'hmac_luby_rackoff_prp'}:
            from .hmac_luby_rackoff_prp import HmacLubyRackoffPRP
            cache['hmaclubyrackoffprp'] = cache['hmac-luby-rackoff-prp'] = cache['hmac_luby_rackoff_prp'] = \
                HmacLubyRackoffPRP
        elif prp_name.lower() in {'bitwise_fpe_prp', 'bitwise-fpe-prp', 'bitwisefpeprp'}:
            from .bitwise_fpe_prp import BitwiseFPEPRP
            cache['bitwise_fpe_prp'] = cache['bitwise-fpe-prp'] = cache['bitwisefpeprp'] = \
                BitwiseFPEPRP
    except ImportError:
        pass  # no extension module, this hash is unsupported.

    prp = cache.get(prp_name.lower())
    if prp is not None:
        return prp

    raise ValueError('unsupported PRP type ' + prp_name)
