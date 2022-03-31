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

from frontend.server.services.service import Service
from toolkit.logger.logger import getSSELogger

logger = getSSELogger("sse_server")


class ServicesManager:
    def __init__(self):
        self.service_dict = {}

    async def create_service(self, sid: str, websocket: WebSocketServerProtocol):
        logger.info(f"A new request for service {sid} found, creating...")
        if sid in self.service_dict:
            await websocket.close()
            reason = f"Service {sid} is already running..."
            logger.error(reason)
            raise ValueError(reason)
        service = Service(sid, websocket)
        self.service_dict[sid] = service
        asyncio.create_task(self.clean_service_when_close_connection(sid, websocket))
        await service.start()  # run forever! do not use asyncio.create_task

    async def clean_service_when_close_connection(self, sid: str, websocket: WebSocketServerProtocol):
        await websocket.wait_closed()
        await asyncio.sleep(5)
        self.service_dict[sid].close_service()
        del self.service_dict[sid]
        logger.info(f"Clean service {sid} successfully.")
