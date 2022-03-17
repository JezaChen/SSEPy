# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License 
@file: connector.py 
@time: 2022/03/14
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""

import asyncio
import pickle

import websockets

from frontend.constants import KEY_SID, KEY_TYPE, TYPE_INIT
from frontend.server.services.services_manager import ServicesManager

_sse_service_manager = ServicesManager()


async def handler(websocket, path):
    """
    Handle a connection and dispatch it according to who is connecting.

    """
    message = await websocket.recv()
    event = pickle.loads(message)
    assert KEY_SID in event and KEY_TYPE in event
    assert event[KEY_TYPE] == TYPE_INIT
    sid = event[KEY_SID]

    await _sse_service_manager.create_service(sid, websocket)


async def main():
    async with websockets.serve(handler, "", 8001, max_size=None):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
