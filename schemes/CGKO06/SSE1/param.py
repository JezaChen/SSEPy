# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: Apache Licence 
@file: param.py 
@time: 2022/03/09
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import math

import toolkit.prf
import toolkit.prp
from toolkit.symmetric_encryption import AESxCBC as PCPASecureSE

PRF = toolkit.prf.get_prf_implementation("HmacPRF")
PRP = toolkit.prp.get_prp_implementation("HmacLubyRackoffPRP")

# todo In the future, it might be possible to switch to the profile form
# GLOBAL PARAMETER
param_k = 24  # key size (bytes)
param_l = 32  # max keyword size (bytes)
param_s = 2 ** 16  # size of array A
param_log2s = int(math.log2(param_s))  # log2(s) (bits)
param_dictionary_size = 2 ** 16  # size of dictionary |∆|
param_identifier_size = 8  # fixed file identifier size (bytes)

# PRF, PRP, SKE Definition, note that key_length param is measured by **bytes**
prf_f = PRF(key_length=param_k, message_length=param_l, output_length=param_k + param_log2s // 8)
prp_pi = PRP(key_length=param_k, message_length=param_l)
prp_psi = PRP(key_length=param_k, message_length=param_log2s // 8)
ske1 = PCPASecureSE(key_length=param_k)
ske2 = PCPASecureSE(key_length=param_k)

SSE1_HEADER = b"\x93\x94Curtomola2006SSE1"
