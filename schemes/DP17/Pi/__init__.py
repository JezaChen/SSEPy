# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: __init__.py.py 
@time: 2022/03/25
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import schemes.interface.module_loader


class ModuleClassLoader(schemes.interface.module_loader.SSEModuleClassLoader):
    _sse_name = "Pi"
    _module_name = "DP17.Pi"


# __init__.py in every SSE module must have sse_module_class_loader attribute
sse_module_class_loader = ModuleClassLoader()
