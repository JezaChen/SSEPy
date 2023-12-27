# -*- coding:utf-8 _*-
"""
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: services_manager.py
@time: 2023/12/17
@contact: jeza@vip.qq.com
@site:
@software: PyCharm
@description:
"""
import asyncio
import pickle
import typing

if typing.TYPE_CHECKING:
    from websockets import WebSocketServerProtocol

__all__ = [
    'send_message',
]


def send_message(
        websocket: 'WebSocketServerProtocol',
        sid: str,
        msg_type: str, content: bytes, **additional_field
) -> asyncio.Task:
    msg_dict = {
        'type': msg_type,
        'sid': sid,
        'content': content
    }
    msg_dict.update(additional_field)
    return asyncio.create_task(websocket.send(pickle.dumps(msg_dict)))
