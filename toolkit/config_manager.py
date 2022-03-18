# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: config_manager.py 
@time: 2022/03/10
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import json


def read_config(config_file_path: str) -> dict:
    with open(config_file_path, "r") as f:
        return json.load(f)


def write_config(config: dict, config_file_path: str):
    with open(config_file_path, "w") as f:
        return json.dump(config, f)
