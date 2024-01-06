# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: service.py 
@time: 2022/03/15
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description:

@note: proxy model, state model
"""
import abc
import asyncio
import pickle

from frontend.common.constants import MsgType
from frontend.common.utils import shorten_sid
from frontend.server.services.comm import send_message
from toolkit.logger.logger import getSSELogger
from websockets.legacy.server import WebSocketServerProtocol

import frontend.server.services.file_manager as FileManager
import schemes

logger = getSSELogger("sse_server")


class SERVICE_STATE:
    NOT_EXISTS = 0
    CONFIG_UPLOADED_BUT_EDB_NOT_UPLOADED = 1
    ALL_READY = 2


class ServiceState(metaclass=abc.ABCMeta):
    """state model, not used currently"""

    def __init__(self):
        self._context = None

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context) -> None:
        self._context = context

    @abc.abstractmethod
    def handle_upload_config(self, context, config: dict):
        pass

    @abc.abstractmethod
    def handle_upload_encrypted_database(self, context, edb_bytes: bytes):
        pass

    @abc.abstractmethod
    def handle_search_request(self, context, token_bytes: bytes):
        pass

    @abc.abstractmethod
    def handle_delete_service(self, context):
        pass


class Service:
    def __init__(self, sid, websocket: WebSocketServerProtocol):
        self.sid = sid
        self.websocket = websocket

        self.config = None  # dict type
        self.config_object = None  # SSEConfig type

        self.sse_scheme = None
        self.sse_module_loader = None
        self.edb = None

        if FileManager.check_sid_folder_exist(sid):
            self.config = FileManager.read_service_config(sid)
            self.service_meta = FileManager.read_service_meta(sid)
            self._load_sse_module()
            self._load_config_object()
        else:  # NEW Service
            self.service_meta = {"state": SERVICE_STATE.NOT_EXISTS}

        self.recv_msg_handler = {
            MsgType.CONFIG: self.handle_upload_config,
            MsgType.UPLOAD_DB: self.handle_upload_encrypted_database,
            MsgType.TOKEN: self.handle_search_token
        }

        if self.get_current_service_state() == SERVICE_STATE.ALL_READY:
            # load SSE
            self._load_sse_module()

        self.send_init_echo()  # Finally, send the echo for initialization message
        logger.info(f"Serve Service {self.short_sid}")

    @property
    def short_sid(self) -> str:
        return shorten_sid(self.sid)

    async def start(self):
        await self._recv_message()

    def _store_service_meta(self):
        FileManager.write_service_meta(self.sid, self.service_meta)

    def send_message(self, msg_type: str, content: bytes, **additional_field):
        send_message(self.websocket, self.sid, msg_type, content, **additional_field)

    async def _recv_message(self):
        async for message_bytes in self.websocket:
            message_dict = pickle.loads(message_bytes)
            msg_type = message_dict.get("type")
            sid = message_dict.get("sid")
            if msg_type is None or sid is None or sid != self.sid:
                continue
            content_byte = message_dict.get("content")
            self.recv_msg_handler[msg_type](content_byte, message_dict)

    def _load_sse_module(self):
        """load SSE module by service config.
        service config must have scheme attribute
        """
        if self.sse_module_loader is not None:
            return

        if self.config is None:
            raise AttributeError(f"The config of this service {self.short_sid} is None.")
        if "scheme" not in self.config:
            raise AttributeError(f"The config of this service {self.short_sid} does not have 'scheme' attribute.")
        scheme_name = self.config["scheme"]
        self.sse_module_loader = schemes.load_sse_module(scheme_name)
        logger.info(f"Load SSE module for service {self.short_sid} successfully.")

    def _load_config_object(self):
        if self.config_object is not None:
            return

        self._load_sse_module()
        self.config_object = self.sse_module_loader.SSEConfig(self.config)  # load scheme config ...
        logger.info(f"Load SSE config for service {self.short_sid} successfully.")

    def _load_sse_scheme(self):
        """load SSE scheme
        @note The SSE module needs to be loaded in advance
        """
        if self.sse_scheme is not None:
            return

        self._load_sse_module()
        self.sse_scheme = self.sse_module_loader.SSEScheme(self.config)  # load scheme construction ...
        logger.info(f"Load SSE scheme for service {self.short_sid} successfully.")

    def _load_sse_encrypted_database(self):
        """load SSE Encrypted Database
        @note The SSE module needs to be loaded in advance
        """
        if self.edb is not None:
            return

        self._load_sse_module()
        self._load_config_object()

        edb_bytes = FileManager.read_encrypted_database(self.sid)
        EDBClass = self.sse_module_loader.SSEEncryptedDatabase
        self.edb = EDBClass.deserialize(edb_bytes, self.config_object)
        logger.info(f"Load SSE encrypted database for service {self.short_sid} successfully.")

    def get_current_service_state(self):
        return self.service_meta["state"]

    def send_init_echo(self):
        self.send_message(MsgType.INIT, pickle.dumps({"ok": True, "state": self.get_current_service_state()}))
        logger.info(f"Send initialization echo of service {self.short_sid}.")

    def handle_upload_config(self, config_bytes: bytes, raw_msg_dict: dict):
        logger.info(f"Receive config file from service {self.short_sid}.")

        if self.get_current_service_state() != SERVICE_STATE.NOT_EXISTS:
            reason = f"The config of service {self.short_sid} has been already uploaded."
            self.send_message(MsgType.CONFIG, pickle.dumps({"ok": False, "reason": reason}))
            logger.error(reason)
            raise ValueError(reason)

        config = pickle.loads(config_bytes)
        # INIT SERVICE
        FileManager.create_sid_folder(self.sid)
        FileManager.write_service_config(self.sid, config)
        self.config = config
        self.service_meta["state"] = SERVICE_STATE.CONFIG_UPLOADED_BUT_EDB_NOT_UPLOADED
        FileManager.write_service_meta(self.sid, self.service_meta)
        self.send_message(MsgType.CONFIG, pickle.dumps({"ok": True}))
        logger.info(f"Store config for service {self.short_sid} successfully.")

    def handle_upload_encrypted_database(self, edb_bytes: bytes, raw_msg_dict: dict):
        logger.info(f"Receive encrypted database from service {self.short_sid}.")

        if self.get_current_service_state() == SERVICE_STATE.NOT_EXISTS:
            reason = f"The config of service {self.short_sid} has not been uploaded."
            self.send_message(MsgType.UPLOAD_DB, pickle.dumps({"ok": False, "reason": reason}))
            logger.error(reason)
            raise ValueError(reason)

        if self.get_current_service_state() == SERVICE_STATE.ALL_READY:
            reason = f"The database of service {self.short_sid} has been already uploaded."
            self.send_message(MsgType.UPLOAD_DB, pickle.dumps({"ok": False, "reason": reason}))
            logger.error(reason)
            raise ValueError(reason)

        FileManager.write_encrypted_database(self.sid, edb_bytes)
        self.service_meta["state"] = SERVICE_STATE.ALL_READY
        FileManager.write_service_meta(self.sid, self.service_meta)
        self.send_message(MsgType.UPLOAD_DB, pickle.dumps({"ok": True}))
        logger.info(f"Store encrypted database for service {self.short_sid} successfully.")

    def handle_search_token(self, token_bytes: bytes, raw_msg_dict: dict):
        logger.info(f"Receive search token from service {self.short_sid}.")

        if self.get_current_service_state() == SERVICE_STATE.NOT_EXISTS:
            reason = f"The config of service {self.short_sid} has not been uploaded."
            self.send_message(MsgType.RESULT, pickle.dumps({"ok": False, "reason": reason}))
            logger.error(reason)
            raise ValueError(reason)

        if self.get_current_service_state() == SERVICE_STATE.CONFIG_UPLOADED_BUT_EDB_NOT_UPLOADED:
            reason = f"The encrypted database of service {self.short_sid} has not been uploaded."
            self.send_message(MsgType.RESULT, pickle.dumps({"ok": False, "reason": reason}))
            logger.error(reason)
            raise ValueError(reason)

        # Lazy load SSE Scheme and database
        self._load_sse_scheme()
        self._load_sse_encrypted_database()

        tk_digest = raw_msg_dict.get("token_digest")
        tk_object = self.sse_module_loader.SSEToken.deserialize(token_bytes, self.config_object)
        result = self.sse_scheme.Search(self.edb, tk_object)
        self.send_message(MsgType.RESULT, content=result.serialize(), token_digest=tk_digest)
        logger.info(f"Search for service {self.short_sid} successfully.")

    def close_service(self):
        self._store_service_meta()

    async def wait_closed(self):
        await self.websocket.wait_closed()
