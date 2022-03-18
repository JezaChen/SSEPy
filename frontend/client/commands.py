# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: commands.py 
@time: 2022/03/18
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: Non-interactive command processing module
This module needs to be responsible for processing commands
and converting data structures into structures that the service can understand
@todo need to wrap service
@todo handle exceptions
"""
import asyncio
import json
import pickle

import schemes
from frontend.client.services.service import Service
from toolkit.config_manager import write_config, read_config
from toolkit.database_utils import convert_database_keyword_to_bytes

__client_service = None


def generate_default_config(scheme_name: str, config_save_path: str):
    try:
        sse_module_loader = schemes.load_sse_module(scheme_name)
    except ValueError:
        print(f">>> Unsupported SSE Scheme {scheme_name}.")
        return

    default_config = sse_module_loader.SSEConfig.get_default_config()
    write_config(default_config, config_save_path)
    print(f">>> Create default config of {scheme_name} successfully.")


def create_service(config_path: str):
    global __client_service

    config = read_config(config_path)
    __client_service = Service()
    try:
        sid = __client_service.handle_create_config(config)
        print(f">>> Create service {sid} successfully.")
    except ValueError as e:
        print(f">>> Create service error: {e}")


def __upload_config_echo_handler(fut: asyncio.Future):
    content = pickle.loads(fut.result())
    if not content.get("ok", False):
        reason = content.get("reason", "")
        print(f">>> Upload config error, reason: {reason}")
        return
    print(f">>> Upload config successfully")


def __upload_encrypted_database_echo_handler(fut: asyncio.Future):
    content = pickle.loads(fut.result())
    if not content.get("ok", False):
        reason = content.get("reason", "")
        print(f">>> Upload encrypted database error, reason: {reason}")
        return
    print(f">>> Upload encrypted database successfully")


def __search_echo_handler(fut: asyncio.Future):
    global __client_service

    if isinstance(__client_service, Service):
        content = fut.result()
        result = __client_service.sse_module_loader.SSEResult.deserialize(content,
                                                                          __client_service.config_object)
        print(f">>> The result is {result}.")


async def upload_config(sid: str):
    global __client_service
    __client_service = Service(sid)

    try:
        await __client_service.handle_upload_config(wait=True,
                                                    wait_callback_func=__upload_config_echo_handler)
    except Exception as e:
        print(f">>> Upload config error, {e}")
    finally:
        await __client_service.close_service()


def generate_key(sid: str):
    global __client_service
    __client_service = Service(sid)

    try:
        __client_service.handle_create_key()
        print(f">>> Generate key successfully.")
    except ValueError as e:
        print(f">>> Generate key error: {e}")


def encrypt_database(sid: str, db_path: str):
    global __client_service
    __client_service = Service(sid)

    with open(db_path, "r") as f:
        db = json.load(f)
        db = convert_database_keyword_to_bytes(db)
        try:
            __client_service.handle_encrypt_database(db)
            print(f">>> Encrypted Database successfully.")
        except ValueError as e:
            print(f">>> Create service error: {e}")


async def upload_encrypted_database(sid: str):
    global __client_service
    __client_service = Service(sid)

    try:
        await __client_service.handle_upload_encrypted_database(wait=True,
                                                                wait_callback_func=__upload_encrypted_database_echo_handler)
    except Exception as e:
        print(f">>> Upload Encrypted Database error: {e}")
    finally:
        await __client_service.close_service()


async def search(sid: str, keyword: str):
    global __client_service
    __client_service = Service(sid)

    try:
        keyword_bytes = bytes(keyword, encoding="utf-8")
        await __client_service.handle_keyword_search(keyword_bytes,
                                                     wait=True,
                                                     wait_callback_func=__search_echo_handler)
    except Exception as e:
        print(f">>> Search error, {e}")
    finally:
        await __client_service.close_service()