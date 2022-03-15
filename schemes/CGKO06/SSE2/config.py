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
import math

import toolkit.config_manager
import toolkit.prp
import toolkit.symmetric_encryption
from schemes.interface.config import SSEConfig
from toolkit.database_utils import get_distinct_file_count


def determine_param_n(db: dict) -> int:
    return get_distinct_file_count(db)


def determine_param_max(max_document_size: int):
    """
    Determine the parameter max in SSE-2, by the max document size
    The essence is to find out how many keywords at most can make up that document of max size.
    Start with single-byte keywords and keep adding up the number of keywords
    :param max_document_size (bytes)
    """
    result = 0
    curr_keyword_size = 1
    curr_document_size = 0

    while True:
        if curr_document_size + 2**(curr_keyword_size *
                                    8) * curr_keyword_size > max_document_size:
            result += (max_document_size -
                       curr_document_size) // curr_keyword_size
            break
        result += 2**(curr_keyword_size * 8)
        curr_document_size += 2**(curr_keyword_size * 8) * curr_keyword_size
        curr_keyword_size += 1

    return result


SSE2_HEADER = b"\x93\x94Curtomola2006SSE2"

# If the param of the specified length is not suffixed, the default is in bytes
# The length parameter of the bit suffix is the length in bits

DEFAULT_CONFIG = {
    "param_k": 24,  # key size (bytes)
    "param_l": 32,  # max keyword size (bytes)
    "param_n": -1,  # number of files
    "param_max":
    -1,  # parameter max, need to be determined at first # todo need document scan
    "param_dictionary_size": 65536,
    "param_identifier_size": 8,
    "param_max_file_size": 1024 * 1024,
    "prp_pi": "BitwiseFPEPRP",
    "ske": "AES-CBC"
}


class SSE2Config(SSEConfig):
    __slots__ = [
        "param_k",
        "param_l",
        "param_n",
        "param_max",
        "param_s",
        "param_k_bits",
        "param_l_bits",
        "param_log2_n",
        "param_log2_n_bytes",
        "param_log2_n_plus_max",
        "param_log2_n_plus_max_bytes",
        "param_dictionary_size",
        "param_identifier_size",
        "param_max_file_size",  # todo need to scan
        "prp_pi",
        "ske"
    ]

    def __init__(self, config_dict: dict):
        super(SSE2Config, self).__init__(config_dict)
        self._parse_config(config_dict)

    def _parse_config(self, config_dict: dict):
        SSEConfig.check_param_exist(
            ["param_k", "param_l", "param_n", "param_max_file_size"],
            config_dict)

        self.param_k = config_dict.get("param_k")
        self.param_l = config_dict.get("param_l")
        self.param_n = config_dict.get("param_n")

        self.param_k_bits = self.param_k * 8
        self.param_l_bits = self.param_l * 8

        self.param_max = determine_param_max(
            config_dict.get("param_max_file_size"))

        self.param_log2_n = math.ceil(math.log2(self.param_n))
        self.param_log2_n_bytes = math.ceil(self.param_log2_n / 8)

        self.param_log2_n_plus_max = math.ceil(
            math.log2(self.param_n + self.param_max))
        self.param_log2_n_plus_max_bytes = math.ceil(
            self.param_log2_n_plus_max / 8)

        self.param_s = self.param_max * self.param_n

        self.prp_pi = toolkit.prp.get_prp_implementation(
            config_dict.get("prp_pi",
                            ""))(key_bit_length=self.param_k_bits,
                                 message_bit_length=self.param_l_bits +
                                 self.param_log2_n_plus_max)
        self.ske = toolkit.symmetric_encryption.get_symmetric_encryption_implementation(
            config_dict.get("ske", ""))(key_length=self.param_k)


def scan_database_and_update_config_dict(config_dict: dict, database: dict):
    config_dict["param_n"] = determine_param_n(database)


if __name__ == '__main__':
    determine_param_max(1000 * 1000)
