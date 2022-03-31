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
            "config": self.handle_upload_config,
            "upload_edb": self.handle_upload_encrypted_database,
            "token": self.handle_search_token
        }

        if self.get_current_service_state() == SERVICE_STATE.ALL_READY:
            # load SSE
            self._load_sse_module()

        self.send_init_echo()  # Finally, send the echo for initialization message
        logger.info(f"Serve Service {self.sid}")

    async def start(self):
        await self._recv_message()

    def _store_service_meta(self):
        FileManager.write_service_meta(self.sid, self.service_meta)

    def _send_message(self, msg_type: str, content: bytes, **additional_field):
        msg_dict = {
            "type": msg_type,
            "sid": self.sid,
            "content": content
        }
        msg_dict.update(additional_field)
        asyncio.create_task(self.websocket.send(pickle.dumps(msg_dict)))

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
            raise AttributeError(f"The config of this service {self.sid} is None.")
        if "scheme" not in self.config:
            raise AttributeError(f"The config of this service {self.sid} does not have 'scheme' attribute.")
        scheme_name = self.config["scheme"]
        self.sse_module_loader = schemes.load_sse_module(scheme_name)
        logger.info(f"Load SSE module for service {self.sid} successfully.")

    def _load_config_object(self):
        if self.config_object is not None:
            return

        self._load_sse_module()
        self.config_object = self.sse_module_loader.SSEConfig(self.config)  # load scheme config ...
        logger.info(f"Load SSE config for service {self.sid} successfully.")

    def _load_sse_scheme(self):
        """load SSE scheme
        @note The SSE module needs to be loaded in advance
        """
        if self.sse_scheme is not None:
            return

        self._load_sse_module()
        self.sse_scheme = self.sse_module_loader.SSEScheme(self.config)  # load scheme construction ...
        logger.info(f"Load SSE scheme for service {self.sid} successfully.")

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
        logger.info(f"Load SSE encrypted database for service {self.sid} successfully.")

    def get_current_service_state(self):
        return self.service_meta["state"]

    def send_init_echo(self):
        self._send_message("init", pickle.dumps({"ok": True, "state": self.get_current_service_state()}))
        logger.info(f"Send initialization echo of service {self.sid}.")

    def handle_upload_config(self, config_bytes: bytes, raw_msg_dict: dict):
        logger.info(f"Receive config file from service {self.sid}.")

        if self.get_current_service_state() != SERVICE_STATE.NOT_EXISTS:
            reason = f"The config of service {self.sid} has been already uploaded."
            self._send_message("config", pickle.dumps({"ok": False, "reason": reason}))
            logger.error(reason)
            raise ValueError(reason)

        config = pickle.loads(config_bytes)
        # INIT SERVICE
        FileManager.create_sid_folder(self.sid)
        FileManager.write_service_config(self.sid, config)
        self.config = config
        self.service_meta["state"] = SERVICE_STATE.CONFIG_UPLOADED_BUT_EDB_NOT_UPLOADED
        FileManager.write_service_meta(self.sid, self.service_meta)
        self._send_message("config", pickle.dumps({"ok": True}))
        logger.info(f"Store config for service {self.sid} successfully.")

    def handle_upload_encrypted_database(self, edb_bytes: bytes, raw_msg_dict: dict):
        logger.info(f"Receive encrypted database from service {self.sid}.")

        if self.get_current_service_state() == SERVICE_STATE.NOT_EXISTS:
            reason = f"The config of service {self.sid} has not been uploaded."
            self._send_message("upload_edb", pickle.dumps({"ok": False, "reason": reason}))
            logger.error(reason)
            raise ValueError(reason)

        if self.get_current_service_state() == SERVICE_STATE.ALL_READY:
            reason = f"The database of service {self.sid} has been already uploaded."
            self._send_message("upload_edb", pickle.dumps({"ok": False, "reason": reason}))
            logger.error(reason)
            raise ValueError(reason)

        FileManager.write_encrypted_database(self.sid, edb_bytes)
        self.service_meta["state"] = SERVICE_STATE.ALL_READY
        FileManager.write_service_meta(self.sid, self.service_meta)
        self._send_message("upload_edb", pickle.dumps({"ok": True}))
        logger.info(f"Store encrypted database for service {self.sid} successfully.")

    def handle_search_token(self, token_bytes: bytes, raw_msg_dict: dict):
        logger.info(f"Receive search token from service {self.sid}.")

        if self.get_current_service_state() == SERVICE_STATE.NOT_EXISTS:
            reason = f"The config of service {self.sid} has not been uploaded."
            self._send_message("result", pickle.dumps({"ok": False, "reason": reason}))
            logger.error(reason)
            raise ValueError(reason)

        if self.get_current_service_state() == SERVICE_STATE.CONFIG_UPLOADED_BUT_EDB_NOT_UPLOADED:
            reason = f"The encrypted database of service {self.sid} has not been uploaded."
            self._send_message("result", pickle.dumps({"ok": False, "reason": reason}))
            logger.error(reason)
            raise ValueError(reason)

        # Lazy load SSE Scheme and database
        self._load_sse_scheme()
        self._load_sse_encrypted_database()

        tk_digest = raw_msg_dict.get("token_digest")
        tk_object = self.sse_module_loader.SSEToken.deserialize(token_bytes, self.config_object)
        result = self.sse_scheme.Search(self.edb, tk_object)
        self._send_message("result", content=result.serialize(), token_digest=tk_digest)
        logger.info(f"Search for service {self.sid} successfully.")

    def close_service(self):
        self._store_service_meta()
