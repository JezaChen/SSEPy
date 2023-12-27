# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: services_manager.py 
@time: 2022/03/15
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import asyncio

from websockets.legacy.server import WebSocketServerProtocol

from frontend.server.services.comm import send_message
from frontend.server.services.service import Service
from toolkit.logger.logger import getSSELogger

logger = getSSELogger("sse_server")


class ServicesManager:
    def __init__(self):
        self._access_dict_lock = asyncio.Lock()
        self._service_dict = {}

    async def create_service(self, sid: str, websocket: WebSocketServerProtocol):
        logger.info(f"A new request for service {sid} found, creating...")
        # initialize a service first
        service = Service(sid, websocket)

        if sid in self._service_dict:
            prev_server = self._service_dict[sid]
            reason = f"Service {sid} is already running, we need to wait for the previous connection to close..."
            logger.warning(reason)
            service.send_message("control", reason.encode('utf8'))
            await prev_server.wait_closed()  # wait for the previous socket to close

        async with self._access_dict_lock:
            self._service_dict[sid] = service
        clean_task = asyncio.create_task(self.clean_service_when_close_connection(sid, websocket))
        await service.start()  # run forever! do not use asyncio.create_task
        await clean_task

    async def clean_service_when_close_connection(self, sid: str, websocket: WebSocketServerProtocol):
        await websocket.wait_closed()
        async with self._access_dict_lock:
            await asyncio.sleep(5)
            self._service_dict[sid].close_service()
            del self._service_dict[sid]
        logger.info(f"Clean service {sid} successfully.")
