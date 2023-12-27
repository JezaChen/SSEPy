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
@note2: Require server response to modify upload status
"""
import asyncio
import functools
import hashlib
import itertools
import os
import pickle

import websockets
import websockets.client
from websockets.exceptions import InvalidURI, InvalidHandshake

import frontend.client.services.file_manager as FileManager
import schemes
from frontend.common.constants import MsgType
# bits represents status
from frontend.constants import KEY_TYPE, KEY_SID, TYPE_INIT
from global_config import ClientConfig
from toolkit.logger.logger import getSSELogger

logger = getSSELogger("sse_client",
                      console_log_level=ClientConfig.CONSOLE_LOG_LEVEL,
                      file_log_level=ClientConfig.FILE_LOG_LEVEL)

_BIT_CONFIG_CREATED = 0b00001
_BIT_CONFIG_UPLOADED = 0b00010
_BIT_KEY_CREATED = 0b00100
_BIT_DB_ENCRYPTED = 0b01000
_BIT_DB_UPLOADED = 0b10000

_EMPTY_STATE = 0b00000


class SERVICE_STATE:
    NOT_EXISTS = 0
    CONFIG_UPLOADED_BUT_EDB_NOT_UPLOADED = 1
    ALL_READY = 2


class ClientServiceState:

    @staticmethod
    def is_config_created(state_bit_set):
        return bool(state_bit_set & _BIT_CONFIG_CREATED)

    @staticmethod
    def is_config_uploaded(state_bit_set):
        return bool(state_bit_set & _BIT_CONFIG_UPLOADED)

    @staticmethod
    def is_key_created(state_bit_set):
        return bool(state_bit_set & _BIT_KEY_CREATED)

    @staticmethod
    def is_db_encrypted(state_bit_set):
        return bool(state_bit_set & _BIT_DB_ENCRYPTED)

    @staticmethod
    def is_db_uploaded(state_bit_set):
        return bool(state_bit_set & _BIT_DB_UPLOADED)

    @staticmethod
    def set_config_created(state_bit_set, is_config_created: bool):
        if is_config_created:
            return state_bit_set | _BIT_CONFIG_CREATED
        else:
            return state_bit_set & ~_BIT_CONFIG_CREATED

    @staticmethod
    def set_config_uploaded(state_bit_set, is_config_uploaded: bool):
        if is_config_uploaded:
            return state_bit_set | _BIT_CONFIG_UPLOADED
        else:
            return state_bit_set & ~_BIT_CONFIG_UPLOADED

    @staticmethod
    def set_key_created(state_bit_set, is_key_created: bool):
        if is_key_created:
            return state_bit_set | _BIT_KEY_CREATED
        else:
            return state_bit_set & ~_BIT_KEY_CREATED

    @staticmethod
    def set_db_encrypted(state_bit_set, is_db_encrypted: bool):
        if is_db_encrypted:
            return state_bit_set | _BIT_DB_ENCRYPTED
        else:
            return state_bit_set & ~_BIT_DB_ENCRYPTED

    @staticmethod
    def set_db_uploaded(state_bit_set, is_db_uploaded: bool):
        if is_db_uploaded:
            return state_bit_set | _BIT_DB_UPLOADED
        else:
            return state_bit_set & ~_BIT_DB_UPLOADED


def _check_config_valid(config: dict):
    def _try_load_sse_scheme(_scheme_name: str):
        return schemes.load_sse_module(_scheme_name)

    scheme_name = config.get("scheme")
    if scheme_name is None:
        raise ValueError("The scheme parameter is required in the configuration")

    try:
        module_loader = _try_load_sse_scheme(scheme_name)
        module_loader.SSEConfig(config)
        return True
    except Exception:
        return False


def _add_salt_to_config(config: dict):
    if "salt" in config:
        return ValueError("The config already has salt value.")

    config["salt"] = os.urandom(32).hex()


def _calculate_sid_by_config_content(config: dict) -> str:
    import hashlib
    config_bytes = pickle.dumps(config)
    config_digest = hashlib.sha256(config_bytes).digest()
    sid = config_digest.hex()
    return sid


class Service:
    def __init__(self, sid=""):
        logger.info("Create a service")

        self.sid = sid
        self.websocket = None

        self.config = None  # dict type
        self.config_object = None  # SSEConfig type

        if FileManager.check_sid_local_file_valid(sid):
            self.config = FileManager.read_service_config(sid)
            self.service_meta = FileManager.read_service_meta(sid)
        else:
            self.service_meta = {"state": _EMPTY_STATE}

        self.sse_scheme = None
        self.sse_module_loader = None
        self.edb = None
        self.key = None

        if ClientServiceState.is_config_created(self.get_current_service_state()):
            # load SSE module if config exists
            self._load_sse_module()
            self._load_config_object()

        self.recv_msg_handler = {
            MsgType.CONFIG: self.handle_upload_config_echo,
            MsgType.UPLOAD_DB: self.handle_upload_encrypted_database_echo,
            MsgType.RESULT: self.handle_result,
            MsgType.CONTROL: self.handle_control_message,
        }

        self.echo_handler = {
            MsgType.CONFIG: [],
            MsgType.UPLOAD_DB: []
        }

        self.echo_futures = {}
        self.result_futures = {}
        logger.info(f"Create a service {sid} successfully.")

    def register_echo_handler_once(self, msg_type: str, handler):
        if msg_type not in self.echo_handler:
            self.echo_handler[msg_type] = []

        self.echo_handler[msg_type].append(handler)
        logger.info(f"[{self.sid}] Register an echo handler for {msg_type}.")

    def register_upload_echo_future_once(self, msg_type: str, fut: asyncio.Future):
        if msg_type not in self.echo_futures:
            self.echo_futures[msg_type] = []

        self.echo_futures[msg_type].append(fut)
        logger.info(f"[{self.sid}] Register an echo future handler for {msg_type}.")

    def register_result_future_once(self, tk_digest: str, fut: asyncio.Future):
        if tk_digest not in self.result_futures:
            self.result_futures[tk_digest] = []
        self.result_futures[tk_digest].append(fut)
        logger.info(f"[{self.sid}] Register an result future handler for token {tk_digest}.")

    async def load_websocket(self):
        if self.websocket is not None:
            return

        uri = ClientConfig.SERVER_URI
        logger.info(f"[{self.sid}] Connecting to server {uri}.")
        # config =
        try:
            websocket = await websockets.client.connect(uri, max_size=None)
            event = {
                KEY_TYPE: TYPE_INIT,
                KEY_SID: self.sid
            }

            await websocket.send(pickle.dumps(event))

            init_echo = await websocket.recv()
            echo_dict = pickle.loads(init_echo)
            if "content" not in echo_dict:
                logger.error(f"[{self.sid}] Init echo error.")
                raise ValueError("Init echo error.")
            echo_content = pickle.loads(echo_dict.get("content"))
            if echo_content.get("ok"):
                logger.info(f"[{self.sid}] Connect to server {uri} successfully.")
                self.websocket = websocket
                asyncio.create_task(self._recv_message())

                server_state = echo_content.get("state", 0)
                logger.info(f"[{self.sid}] The service status on the server side is {server_state}")
                self.update_current_client_service_state_by_server_service_state(server_state)
            else:
                logger.error(f"[{self.sid}] Init echo error.")
                raise ValueError("Init echo error.")
        except (InvalidURI, InvalidHandshake, TimeoutError, websockets.ConnectionClosed) as e:
            reason = f"[{self.sid}] Init echo error: {e}"
            logger.error(reason)
            raise ValueError(reason)

    def _store_service_meta(self):
        FileManager.write_service_meta(self.sid, self.service_meta)
        logger.info(f"[{self.sid}] Store meta successfully.")

    async def _send_message(self, msg_type: str, content: bytes, **additional_field):
        await self.load_websocket()  # check if websocket is initialized
        msg_dict = {
            "type": msg_type,
            "sid": self.sid,
            "content": content
        }
        msg_dict.update(additional_field)
        await self.websocket.send(pickle.dumps(msg_dict))

    async def _recv_message(self):
        async for message_bytes in self.websocket:
            message_dict = pickle.loads(message_bytes)
            msg_type = message_dict.get("type")
            sid = message_dict.get("sid")
            if msg_type is None or sid is None or sid != self.sid:
                continue
            content_byte = message_dict.get("content")
            self.recv_msg_handler[msg_type](content_byte)

            # echo handler
            if self.echo_handler.get(msg_type):
                for handler in self.echo_handler.get(msg_type, []):
                    handler(content_byte)
                self.echo_handler[msg_type] = []  # clear

            # echo future handler
            if self.echo_futures.get(msg_type):
                for fut in self.echo_futures.get(msg_type, []):
                    fut.set_result(content_byte)
                self.echo_futures[msg_type] = []  # clear

            # result future handler
            if msg_type == MsgType.RESULT:
                token_digest = message_dict.get("token_digest")
                for fut in self.result_futures.get(token_digest, []):
                    fut.set_result(content_byte)
                self.result_futures[token_digest] = []

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
        logger.info(f"[{self.sid}] Load SSE Module successfully.")

    def _load_config_object(self):
        if self.config_object is not None:
            return

        self._load_sse_module()
        self.config_object = self.sse_module_loader.SSEConfig(self.config)  # load scheme config ...
        logger.info(f"[{self.sid}] Load SSE config object successfully.")

    def _load_sse_scheme(self):
        """load SSE scheme
        @note The SSE module needs to be loaded in advance
        """
        if self.sse_scheme is not None:
            return

        self._load_sse_module()
        self.sse_scheme = self.sse_module_loader.SSEScheme(self.config)  # load scheme construction ...
        logger.info(f"[{self.sid}] Load SSE scheme successfully.")

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
        logger.info(f"[{self.sid}] Load SSE encrypted database successfully.")

    def _load_sse_key(self):
        self._load_sse_module()
        self._load_config_object()

        key_bytes = FileManager.read_key(self.sid)
        KeyClass = self.sse_module_loader.SSEKey
        self.key = KeyClass.deserialize(key_bytes, self.config_object)
        logger.info(f"[{self.sid}] Load SSE Key successfully.")

    def get_current_service_state(self):
        if self.service_meta is None:
            return _EMPTY_STATE
        return self.service_meta["state"]

    def set_current_service_state(self, new_state):
        self.service_meta["state"] = new_state

    def update_current_client_service_state_by_server_service_state(self, service_state):
        # todo can be optimized
        if service_state == SERVICE_STATE.NOT_EXISTS:
            self.set_current_service_state(
                ClientServiceState.set_config_uploaded(self.get_current_service_state(), False))
            self.set_current_service_state(
                ClientServiceState.set_db_uploaded(self.get_current_service_state(), False))
        elif service_state == SERVICE_STATE.CONFIG_UPLOADED_BUT_EDB_NOT_UPLOADED:
            self.set_current_service_state(
                ClientServiceState.set_config_uploaded(self.get_current_service_state(), True))
            self.set_current_service_state(
                ClientServiceState.set_db_uploaded(self.get_current_service_state(), False))
        elif service_state == SERVICE_STATE.ALL_READY:
            self.set_current_service_state(
                ClientServiceState.set_config_uploaded(self.get_current_service_state(), True))
            self.set_current_service_state(
                ClientServiceState.set_db_uploaded(self.get_current_service_state(), True))

    def handle_create_config(self, config: dict):
        if ClientServiceState.is_config_created(self.get_current_service_state()):
            raise ValueError(f"The config of service {self.sid} has been already created.")

        _check_config_valid(config)
        _add_salt_to_config(config)  # add salt

        # INIT SERVICE
        self.sid = _calculate_sid_by_config_content(config)  # generated sid
        FileManager.create_sid_folder(self.sid)
        FileManager.write_service_config(self.sid, config)
        self.config = config
        self.set_current_service_state(ClientServiceState.set_config_created(self.get_current_service_state(), True))
        self._store_service_meta()
        logger.info(f"[{self.sid}] Create service {self.sid} successfully!")
        return self.sid

    def _default_upload_config_echo_future_handler(self, fut: asyncio.Future):
        content = fut.result()
        if not content.get("ok", False):
            reason = content.get("reason", "")
            logger.error(f"[{self.sid}] Upload config error, reason: {reason}")
            return
        logger.info(f"[{self.sid}] Upload config successfully")

    def _default_upload_encrypted_database_echo_future_handler(self, fut: asyncio.Future):
        content = fut.result()
        if not content.get("ok", False):
            reason = content.get("reason", "")
            logger.error(f"[{self.sid}] Upload encrypted database error, reason: {reason}")
            return
        logger.info(f"[{self.sid}] Upload encrypted database successfully")

    async def handle_upload_config(self,
                                   wait=False,
                                   wait_callback_func=None):
        # todo echo处理函数能不能整合在wait_callback_func里面去呢，而不用两个处理逻辑
        await self.load_websocket()

        if ClientServiceState.is_config_uploaded(self.get_current_service_state()):
            reason = f"The config of service {self.sid} has been already uploaded."
            logger.error(reason)
            raise ValueError(reason)
        if not ClientServiceState.is_config_created(self.get_current_service_state()):
            reason = f"The config of service {self.sid} is not found."
            logger.error(reason)
            raise ValueError(reason)

        fut = None
        if wait:
            if wait_callback_func is None:
                wait_callback_func = self._default_upload_config_echo_future_handler

            # Get the current event loop.
            loop = asyncio.get_running_loop()
            # Create a new Future object.
            fut = loop.create_future()
            fut.add_done_callback(wait_callback_func)
            self.register_upload_echo_future_once(MsgType.CONFIG, fut)

        await self._send_message(MsgType.CONFIG, pickle.dumps(self.config))
        logger.info(f"[{self.sid}] Uploading config.")

        if wait:
            await asyncio.wait_for(fut, 60)

    def handle_upload_config_echo(self, content_bytes: bytes):
        content = pickle.loads(content_bytes)
        if not content.get("ok", False):
            reason = content.get("reason", "")
            logger.error(f"[{self.sid}] Upload config error, reason: {reason}")
            return

        self.set_current_service_state(ClientServiceState.set_config_uploaded(self.get_current_service_state(), True))
        self._store_service_meta()
        logger.info(f"[{self.sid}] Upload config successfully")

    def handle_upload_encrypted_database_echo(self, content_bytes: bytes):
        content = pickle.loads(content_bytes)
        if not content.get("ok", False):
            reason = content.get("reason", "")
            logger.error(f"[{self.sid}] Upload encrypted database error, reason: {reason}")
            return

        self.set_current_service_state(ClientServiceState.set_db_uploaded(self.get_current_service_state(), True))
        self._store_service_meta()
        logger.info(f"[{self.sid}] Upload encrypted database successfully")
        FileManager.delete_encrypted_database(self.sid)
        logger.info(f"[{self.sid}] Delete the local encrypted database successfully")

    def handle_create_key(self):
        if ClientServiceState.is_key_created(self.get_current_service_state()):  # todo should allow re-create
            reason = f"The SSE key of service {self.sid} has been already created."
            logger.error(reason)
            raise ValueError(reason)
        if not ClientServiceState.is_config_created(self.get_current_service_state()):
            reason = f"The config of service {self.sid} is not found."
            logger.error(reason)
            raise ValueError(reason)

        self._load_config_object()
        self._load_sse_scheme()
        sse_key = self.sse_scheme.KeyGen()
        FileManager.write_key(self.sid, sse_key.serialize())
        self.set_current_service_state(ClientServiceState.set_key_created(self.get_current_service_state(), True))
        self._store_service_meta()

    def handle_encrypt_database(self, database: dict):
        if ClientServiceState.is_db_encrypted(self.get_current_service_state()):  # todo should allow re-create
            reason = f"The database of service {self.sid} has been already created."
            logger.error(reason)
            raise ValueError(reason)
        if not ClientServiceState.is_config_created(self.get_current_service_state()):
            reason = f"The config of service {self.sid} is not found."
            logger.error(reason)
            raise ValueError(reason)
        if not ClientServiceState.is_key_created(self.get_current_service_state()):
            reason = f"The key of service {self.sid} is not found."
            logger.error(reason)
            raise ValueError(reason)

        self._load_sse_scheme()
        self._load_sse_key()
        self.edb = self.sse_scheme.EDBSetup(self.key, database)
        FileManager.write_encrypted_database(self.sid, self.edb.serialize())
        self.set_current_service_state(ClientServiceState.set_db_encrypted(self.get_current_service_state(), True))
        self._store_service_meta()

    async def handle_upload_encrypted_database(self,
                                               wait=False,
                                               wait_callback_func=None):

        await self.load_websocket()

        if ClientServiceState.is_db_uploaded(self.get_current_service_state()):
            reason = f"The database of service {self.sid} has been already uploaded."
            logger.error(reason)
            raise ValueError(reason)
        if not ClientServiceState.is_config_uploaded(self.get_current_service_state()):
            reason = f"The config of service {self.sid} has not been uploaded."
            logger.error(reason)
            raise ValueError(reason)
        if not ClientServiceState.is_key_created(self.get_current_service_state()):
            reason = f"The key of service {self.sid} is not found."
            logger.error(reason)
            raise ValueError(reason)

        self._load_sse_encrypted_database()

        fut = None
        if wait:
            if wait_callback_func is None:
                wait_callback_func = self._default_upload_encrypted_database_echo_future_handler
            # Get the current event loop.
            loop = asyncio.get_running_loop()
            # Create a new Future object.
            fut = loop.create_future()
            fut.add_done_callback(wait_callback_func)
            self.register_upload_echo_future_once(MsgType.UPLOAD_DB, fut)

        await self._send_message(MsgType.UPLOAD_DB, self.edb.serialize())
        logger.info(f"[{self.sid}] Uploading encrypted database.")

        if wait:
            await asyncio.wait_for(fut, 60)

    async def handle_keyword_search(self, keyword: bytes,
                                    wait=False,
                                    wait_callback_func=None):
        await self.load_websocket()

        if not ClientServiceState.is_db_uploaded(self.get_current_service_state()):
            reason = f"The database of service {self.sid} has not been uploaded."
            logger.error(reason)
            raise ValueError(reason)

        self._load_sse_scheme()
        self._load_sse_key()

        fut = None
        if wait:
            if wait_callback_func is None:
                wait_callback_func = self.handle_result_future
            # Get the current event loop.
            loop = asyncio.get_running_loop()
            # Create a new Future object.
            fut = loop.create_future()
            fut.add_done_callback(wait_callback_func)
            self.register_upload_echo_future_once(MsgType.RESULT, fut)

        token = self.sse_scheme.TokenGen(self.key, keyword)
        token_bytes = token.serialize()
        token_digest = hashlib.sha256(token_bytes).digest()

        await self._send_message(MsgType.TOKEN,
                                 token_bytes,
                                 token_digest=token_digest)
        logger.info(f"[{self.sid}] Uploading search token.")

        if wait:
            await asyncio.wait_for(fut, 60)

    def handle_result(self, result_bytes: bytes):
        result = self.sse_module_loader.SSEResult.deserialize(result_bytes, self.config_object)
        logger.info(f"[{self.sid}] The result is {result}.")
        return result

    def handle_result_future(self, fut: asyncio.Future):
        content = fut.result()
        result = self.sse_module_loader.SSEResult.deserialize(content, self.config_object)
        logger.info(f"[{self.sid}] The result is {result}.")

    def handle_control_message(self, msg_bytes: bytes):
        msg_str = msg_bytes.decode(encoding='utf8')
        logger.warning(f"[{self.sid}] Receive control message: {msg_str}.")

    async def close_service(self):
        self._store_service_meta()
        if self.websocket is not None:
            await self.websocket.close()
        logger.info(f"[{self.sid}] close Service successfully.")


async def main():
    # simple test
    from schemes.CJJ14.PiBas.config import DEFAULT_CONFIG as PI_BAS_DEFAULT_CONFIG

    service = Service()

    from test.tools.faker import fake_db_for_inverted_index_based_sse
    from test.test_sse_schemes.test_CJJ14_PiBas import TEST_KEYWORD_SIZE
    from test.test_sse_schemes.test_CJJ14_PiBas import TEST_FILE_ID_SIZE

    db = fake_db_for_inverted_index_based_sse(TEST_KEYWORD_SIZE,
                                              TEST_FILE_ID_SIZE,
                                              1000,
                                              db_w_size_range=(1, 200))
    service.handle_create_config(PI_BAS_DEFAULT_CONFIG)
    service.handle_create_key()
    service.handle_encrypt_database(db)
    await service.handle_upload_config(wait=True)

    while True:
        if ClientServiceState.is_config_uploaded(service.get_current_service_state()):
            break
        await asyncio.sleep(1)

    await service.handle_upload_encrypted_database(wait=True)

    while True:
        if ClientServiceState.is_db_uploaded(service.get_current_service_state()):
            break
        await asyncio.sleep(1)

    def _compare_result(fut: asyncio.Future, actual_result):
        from schemes.CJJ14.PiBas.structures import PiBasResult
        return_result_bytes = fut.result()
        return_result = PiBasResult.deserialize(return_result_bytes)
        assert return_result.result == actual_result

    for keyword in itertools.islice(db.keys(), 10):
        # service.register_echo_handler_once(MsgType.RESULT, functools.partial(_compare_result, actual_result=db[keyword]))
        await service.handle_keyword_search(keyword,
                                            wait=True,
                                            wait_callback_func=functools.partial(_compare_result,
                                                                                 actual_result=db[keyword]))

    await service.close_service()


async def main2():
    # simple test
    from schemes.CJJ14.PiBas.config import DEFAULT_CONFIG as PI_BAS_DEFAULT_CONFIG

    service = Service()

    from test.tools.faker import fake_db_for_inverted_index_based_sse
    from test.test_sse_schemes.test_CJJ14_PiBas import TEST_KEYWORD_SIZE
    from test.test_sse_schemes.test_CJJ14_PiBas import TEST_FILE_ID_SIZE

    db = fake_db_for_inverted_index_based_sse(TEST_KEYWORD_SIZE,
                                              TEST_FILE_ID_SIZE,
                                              1000,
                                              db_w_size_range=(1, 200))
    service.handle_create_config(PI_BAS_DEFAULT_CONFIG)
    service.handle_create_key()
    service.handle_encrypt_database(db)
    await service.handle_upload_config(wait=True)
    await service.close_service()


if __name__ == "__main__":
    asyncio.run(main())
