# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: module_loader.py
@time: 2022/03/16
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: SSE Module & Class Loader
"""
import abc
import importlib

_CONSTRUCTION_MODULE_NAME = ".construction"
_STRUCTURE_MODULE_NAME = ".structures"
_CONFIG_MODULE_NAME = ".config"
"""Concrete Class Name = sse name + class suffix"""
_CONFIG_CLASS_SUFFIX = "Config"
_KEY_CLASS_SUFFIX = "Key"
_ENCRYPTED_DATABASE_CLASS_SUFFIX = "EncryptedDatabase"
_TOKEN_CLASS_SUFFIX = "Token"
_RESULT_CLASS_SUFFIX = "Result"

SCHEMES_MODULE_PATH = "schemes"


class SSEModuleClassLoader:
    _sse_name = ""  # need to be overwritten!
    _module_name = ""  # need to be overwritten!

    _construction_module = None
    _structure_module = None
    _config_module_module = None

    def _load_construction_module(self):
        actual_path = "{}.{}".format(SCHEMES_MODULE_PATH, self._module_name)
        if self._construction_module is None:
            self._construction_module = importlib.import_module(
                _CONSTRUCTION_MODULE_NAME, actual_path)

    def _load_structure_module(self):
        actual_path = "{}.{}".format(SCHEMES_MODULE_PATH, self._module_name)
        if self._structure_module is None:
            self._structure_module = importlib.import_module(
                _STRUCTURE_MODULE_NAME, actual_path)

    def _load_config_module(self):
        actual_path = "{}.{}".format(SCHEMES_MODULE_PATH, self._module_name)
        if self._config_module_module is None:
            self._config_module_module = importlib.import_module(
                _CONFIG_MODULE_NAME, actual_path)

    @property
    def SSEScheme(self):
        self._load_construction_module()
        class_name = self._sse_name

        if not hasattr(self._construction_module, class_name):
            raise ValueError(
                f"The construction class of SSE Scheme {self._sse_name} Load Error."
            )
        return getattr(self._construction_module, class_name)

    @property
    def SSEConfig(self):
        self._load_config_module()
        class_name = self._sse_name + _CONFIG_CLASS_SUFFIX

        if not hasattr(self._config_module_module, class_name):
            raise ValueError(
                f"The config class of SSE Scheme {self._sse_name} Load Error.")
        return getattr(self._config_module_module, class_name)

    @property
    def SSEKey(self):
        self._load_structure_module()
        class_name = self._sse_name + _KEY_CLASS_SUFFIX

        if not hasattr(self._structure_module, class_name):
            raise ValueError(
                f"The key class of SSE Scheme {self._sse_name} Load Error.")
        return getattr(self._structure_module, class_name)

    @property
    def SSEEncryptedDatabase(self):
        self._load_structure_module()
        class_name = self._sse_name + _ENCRYPTED_DATABASE_CLASS_SUFFIX

        if not hasattr(self._structure_module, class_name):
            raise ValueError(
                f"The encrypted database class of SSE Scheme {self._sse_name} Load Error."
            )
        return getattr(self._structure_module, class_name)

    @property
    def SSEToken(self):
        self._load_structure_module()
        class_name = self._sse_name + _TOKEN_CLASS_SUFFIX

        if not hasattr(self._structure_module, class_name):
            raise ValueError(
                f"The token class of SSE Scheme {self._sse_name} Load Error.")
        return getattr(self._structure_module, class_name)

    @property
    def SSEResult(self):
        self._load_structure_module()
        class_name = self._sse_name + _RESULT_CLASS_SUFFIX

        if not hasattr(self._structure_module, class_name):
            raise ValueError(
                f"The result class of SSE Scheme {self._sse_name} Load Error.")
        return getattr(self._structure_module, class_name)
