# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: config.py 
@time: 2022/03/12
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import math

import toolkit.config_manager
import toolkit.prf
import toolkit.prp
import toolkit.symmetric_encryption
from schemes.interface.config import SSEConfig

SSE1_HEADER = b"\x93\x94Curtomola2006SSE1"

# If the param of the specified length is not suffixed, the default is in bytes
# The length parameter of the bit suffix is the length in bits

DEFAULT_CONFIG = {
    "scheme": "CGKO06.SSE1",
    "param_k": 24,  # key size (bytes)
    "param_l": 32,  # max keyword size (bytes)
    "param_s": 2 ** 16,  # size of array A
    "param_dictionary_size": 2 ** 16,  # size of dictionary |∆|
    "param_identifier_size": 8,  # fixed file identifier size (bytes)

    "prf_f": "HmacPRF",
    "prp_pi": "BitwiseFPEPRP",  # todo 最好按照prp的格式识别使用哪个参数(bit version or byte version)
    "prp_psi": "BitwiseFPEPRP",
    "ske1": "AES-CBC",
    "ske2": "AES-CBC",
}


class SSE1Config(SSEConfig):
    __slots__ = [
        "param_k",
        "param_l",
        "param_s",

        "param_k_bits",
        "param_l_bits",
        "param_log2_s",
        "param_log2_s_bytes",

        "param_dictionary_size",
        "param_identifier_size",

        "prp_pi",
        "prp_psi",
        "prf_f",
        "ske1",
        "ske2"
    ]

    def __init__(self, config_dict: dict):
        super(SSE1Config, self).__init__(config_dict)
        self._parse_config(config_dict)

    def _parse_config(self, config_dict: dict):
        SSEConfig.check_param_exist(["param_k", "param_l", "param_s",
                                     "param_dictionary_size", "param_identifier_size",
                                     "prp_pi", "prp_psi", "prf_f", "ske1", "ske2"],
                                    config_dict)

        self.param_k = config_dict.get("param_k")
        self.param_l = config_dict.get("param_l")
        self.param_s = config_dict.get("param_s")

        self.param_identifier_size = config_dict.get("param_identifier_size")
        self.param_dictionary_size = config_dict.get("param_dictionary_size")

        self.param_k_bits = self.param_k * 8
        self.param_l_bits = self.param_l * 8
        self.param_log2_s = math.ceil(math.log2(self.param_s))
        self.param_log2_s_bytes = math.ceil(self.param_log2_s / 8)

        self.prp_pi = toolkit.prp.get_prp_implementation(config_dict.get("prp_pi", ""))(
            key_bit_length=self.param_k_bits,
            message_bit_length=self.param_l_bits
        )
        self.prp_psi = toolkit.prp.get_prp_implementation(config_dict.get("prp_psi", ""))(
            key_bit_length=self.param_k_bits,
            message_bit_length=self.param_log2_s
        )
        self.prf_f = toolkit.prf.get_prf_implementation(config_dict.get("prf_f", ""))(
            key_length=self.param_k,
            message_length=self.param_l,
            output_length=self.param_k + self.param_log2_s_bytes)
        self.ske1 = toolkit.symmetric_encryption.get_symmetric_encryption_implementation(config_dict.get("ske1", ""))(
            key_length=self.param_k
        )
        self.ske2 = toolkit.symmetric_encryption.get_symmetric_encryption_implementation(config_dict.get("ske2", ""))(
            key_length=self.param_k
        )
