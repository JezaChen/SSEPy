# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: config.py
@time: 2022/03/25
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""

import toolkit.config_manager
import toolkit.hash
import toolkit.prf
import toolkit.prp
import toolkit.symmetric_encryption
from schemes.interface.config import SSEConfig

PI_HEADER = b"\x93\x94Demertzis2017LocalityPi"

# If the param of the specified length is not suffixed, the default is in bytes
# The length parameter of the bit suffix is the length in bits

DEFAULT_CONFIG = {
    "scheme": "DP17.Pi",
    "param_lambda": 32,  # key space K

    # Instead of using the parameter s,
    # we use a ratio to indicate the actual number of layers stored.
    "param_actual_storage_level_ratio": 0.2,

    # "param_s": 7,  # level count
    "param_L": 1,  # tunable locality
    "param_identifier_size": 8,
    "rnd": "AES-CBC",
    "prf_f": "HmacPRF",
    "hash_h": "SHA1"
}


class PiConfig(SSEConfig):
    __slots__ = [
        "param_lambda", "param_s", "param_L", "param_identifier_size", "rnd",
        "prf_f", "hash_h", "param_identifier_cipher_len",
        "param_hash_h_digest_size"
    ]

    DEFAULT_CONFIG = DEFAULT_CONFIG

    def __init__(self, config_dict: dict):
        super(PiConfig, self).__init__(config_dict)
        self._parse_config(config_dict)

    def _parse_config(self, config_dict: dict):
        SSEConfig.check_param_exist([
            "param_lambda", "param_actual_storage_level_ratio", "param_L",
            "param_identifier_size", "rnd", "prf_f", "hash_h"
        ], config_dict)

        self.param_lambda = config_dict.get("param_lambda")
        self.param_actual_storage_level_ratio = config_dict.get(
            "param_actual_storage_level_ratio")
        self.param_L = config_dict.get("param_L")
        self.param_identifier_size = config_dict.get("param_identifier_size")

        self.rnd = toolkit.symmetric_encryption.get_symmetric_encryption_implementation(
            config_dict.get("rnd", ""))(key_length=self.param_lambda)

        self.prf_f = toolkit.prf.get_prf_implementation(
            config_dict.get("prf_f", ""))(key_length=self.param_lambda,
                                          output_length=self.param_lambda)

        self.hash_h = toolkit.hash.get_hash_implementation(
            config_dict.get("hash_h", ""))()

        self.param_identifier_cipher_len = len(
            self.rnd.Encrypt(
                b"\x00" * self.param_lambda,
                b"\x00" * (self.param_identifier_size + self.param_lambda)))
        self.param_hash_h_digest_size = self.hash_h.output_length
