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

PI_2LEV_HEADER = b"\x93\x94Cash2014Pi2Lev"

LEVEL_FILE_IDENTIFIER = b"\x00"  # current level is storing file identifiers
LEVEL_POINTER_OF_ARRAY = b"\x01"  # current level is storing pointers of array A

# If the param of the specified length is not suffixed, the default is in bytes
# The length parameter of the bit suffix is the length in bits

DEFAULT_CONFIG = {
    "param_lambda": 32,  # key size (bytes)
    "param_B": 64,  # store identifiers in the array (in the medium and large cases), it packs up to B of them together
    "param_b": 64,  # store identifiers in the dictionary (in the small case), it packs up to b of them together
    "param_B_prime": 64,  # storing pointers
    "param_b_prime": 64,  # storing pointers
    "param_identifier_size": 8,
    "prf_f_output_length": 32,

    "prf_f": "HmacPRF",
    "ske": "AES-CBC"
}


class Pi2LevConfig(SSEConfig):
    __slots__ = [
        "param_lambda",
        "param_B",
        "param_B_prime",
        "param_b",
        "param_b_prime",
        "prf_f_output_length",
        "param_identifier_size",
        "param_index_size_of_A",
        "prf_f",
        "ske"
    ]

    def __init__(self, config_dict: dict):
        super(Pi2LevConfig, self).__init__(config_dict)
        self._parse_config(config_dict)

    def _parse_config(self, config_dict: dict):
        SSEConfig.check_param_exist(["param_lambda",
                                     "param_B",
                                     "param_b",
                                     "param_B_prime",
                                     "param_b_prime",
                                     "prf_f_output_length",
                                     "param_identifier_size",
                                     "prf_f",
                                     "ske"],
                                    config_dict)

        self.param_lambda = config_dict.get("param_lambda")

        self.param_B = config_dict.get("param_B")
        self.param_b = config_dict.get("param_b")

        self.param_B_prime = config_dict.get("param_B_prime")
        self.param_b_prime = config_dict.get("param_b_prime")

        self.prf_f_output_length = config_dict.get("prf_f_output_length")
        self.param_identifier_size = config_dict.get("param_identifier_size")

        self.param_index_size_of_A = (self.param_B * self.param_identifier_size) // self.param_B_prime
        if (self.param_b * self.param_identifier_size) // self.param_b_prime != self.param_index_size_of_A:
            raise ValueError("guarantee (param_B * param_identifier_size) // param_B_prime == "
                             "(param_b * param_identifier_size) // param_b_prime")

        self.prf_f = toolkit.prf.get_prf_implementation(config_dict.get("prf_f", ""))(
            key_length=self.param_lambda,
            output_length=self.prf_f_output_length)

        self.ske = toolkit.symmetric_encryption.get_symmetric_encryption_implementation(config_dict.get("ske", ""))(
            key_length=self.param_lambda
        )
