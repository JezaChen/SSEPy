# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: config.py 
@time: 2022/03/11
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import abc
import json


class SSEConfig(metaclass=abc.ABCMeta):

    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def _parse_config(self, config_dict: dict):
        return

    def to_json(self):
        config_dict = {key: getattr(self, key) for key in self.__slots__}
        return json.dumps(config_dict, indent=4)

    @classmethod
    def from_json(cls, json_str: str):
        config_dict = json.loads(json_str)
        return cls(config_dict)

    def to_dict(self):
        config_dict = {key: getattr(self, key) for key in self.__slots__}
        return config_dict

    @classmethod
    def from_dict(cls, config_dict: dict):
        return cls(config_dict)

    @staticmethod
    def check_param_exist(param_field_to_check: list, config_dict: dict):
        for param_field in param_field_to_check:
            if config_dict.get(param_field, -1) == -1:
                raise ValueError("Parameter {} is missing".format(param_field))

    def __getitem__(self, item):
        return getattr(self, item)
