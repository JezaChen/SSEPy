# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
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

PI_PTR_HEADER = b"\x93\x94Cash2014PiPtr"

# If the param of the specified length is not suffixed, the default is in bytes
# The length parameter of the bit suffix is the length in bits

DEFAULT_CONFIG = {
    "param_lambda": 32,  # key size (bytes)
    "param_B": 64,  # a fixed block size, process B identifiers at a time and pack them into one ciphertext d
    "param_b": 64,  # store encrypted blocks of b pointers to these encrypted blocks
    "param_identifier_size": 8,
    "prf_f_output_length": 32,

    "prf_f": "HmacPRF",
    "ske": "AES-CBC"
}


class PiPtrConfig(SSEConfig):
    __slots__ = [
        "param_lambda",
        "param_B",
        "param_b",
        "prf_f_output_length",
        "param_identifier_size",

        "prf_f",
        "ske"
    ]

    def __init__(self, config_dict: dict):
        super(PiPtrConfig, self).__init__(config_dict)
        self._parse_config(config_dict)

    def _parse_config(self, config_dict: dict):
        SSEConfig.check_param_exist(["param_lambda",
                                     "param_B",
                                     "param_b",
                                     "prf_f_output_length",
                                     "param_identifier_size",
                                     "prf_f",
                                     "ske"],
                                    config_dict)

        self.param_lambda = config_dict.get("param_lambda")
        self.param_B = config_dict.get("param_B")
        self.param_b = config_dict.get("param_b")
        self.prf_f_output_length = config_dict.get("prf_f_output_length")
        self.param_identifier_size = config_dict.get("param_identifier_size")

        self.prf_f = toolkit.prf.get_prf_implementation(config_dict.get("prf_f", ""))(
            key_length=self.param_lambda,
            output_length=self.prf_f_output_length)

        self.ske = toolkit.symmetric_encryption.get_symmetric_encryption_implementation(config_dict.get("ske", ""))(
            key_length=self.param_lambda
        )
