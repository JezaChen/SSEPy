# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: list_utils.py 
@time: 2022/03/29
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
