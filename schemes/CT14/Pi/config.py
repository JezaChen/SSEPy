# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: config.py
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""

import toolkit.config_manager
import toolkit.prf
import toolkit.prp
import toolkit.symmetric_encryption
from schemes.interface.config import SSEConfig

PI_HEADER = b"\x93\x94Cash2014LocalityPi"

# If the param of the specified length is not suffixed, the default is in bytes
# The length parameter of the bit suffix is the length in bits

DEFAULT_CONFIG = {
    "scheme": "CT14.Pi",
    "param_k": 32,  # key space K
    "param_k_prime": 32,  # key space K'
    "param_l": 32,  # key size (bytes)
    # "param_t": -1,  # need to scan, N = 2 ^ t, N is the total size of database
    "param_identifier_size": 4,
    "prf_f": "HmacPRF",
    "prf_f_prime": "HmacPRF",
    "ske": "AES-CBC"
}


class PiConfig(SSEConfig):
    __slots__ = [
        "param_k", "param_k_prime", "param_l", "param_identifier_size",
        "prf_f", "prf_f_prime", "ske"
    ]

    DEFAULT_CONFIG = DEFAULT_CONFIG

    def __init__(self, config_dict: dict):
        super(PiConfig, self).__init__(config_dict)
        self._parse_config(config_dict)

    def _parse_config(self, config_dict: dict):
        SSEConfig.check_param_exist([
            "param_k", "param_k_prime", "param_l", "param_identifier_size",
            "prf_f", "prf_f_prime", "ske"
        ], config_dict)

        self.param_k = config_dict.get("param_k")
        self.param_k_prime = config_dict.get("param_k_prime")
        self.param_l = config_dict.get("param_l")
        # self.param_t = config_dict.get("param_t")

        self.param_identifier_size = config_dict.get("param_identifier_size")

        self.prf_f = toolkit.prf.get_prf_implementation(
            config_dict.get("prf_f", ""))(key_length=self.param_k,
                                          output_length=self.param_k +
                                          self.param_k_prime)

        self.prf_f_prime = toolkit.prf.get_prf_implementation(
            config_dict.get("prf_f_prime", ""))(key_length=self.param_k,
                                                output_length=self.param_l)

        self.ske = toolkit.symmetric_encryption.get_symmetric_encryption_implementation(
            config_dict.get("ske", ""))(key_length=self.param_k_prime)
