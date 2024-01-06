# -*- coding:utf-8 _*-
"""
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: services_manager.py
@time: 2024/1/6
@contact: jeza@vip.qq.com
@site:
@software: PyCharm
@description: utility functions for frontend module
"""

__all__ = [
    'shorten_sid',
]


def shorten_sid(sid: str) -> str:
    """
    shorten sid for display
    :param sid: Service ID
    :return:
    """
    return sid[:8]
