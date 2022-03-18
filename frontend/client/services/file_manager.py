# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: file_manager.py 
@time: 2022/03/15
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import json
import pathlib
import pickle
import shutil

_PROGRAM_DIR_PATH = pathlib.Path.home().joinpath(".sse/client/")
_PROGRAM_PATH = pathlib.Path(_PROGRAM_DIR_PATH)
if not _PROGRAM_PATH.exists():
    _PROGRAM_PATH.mkdir(exist_ok=True, parents=True)


def check_sid_local_file_valid(sid: str):
    return _PROGRAM_PATH.joinpath(sid).exists() \
        and _PROGRAM_PATH.joinpath(sid).joinpath("config.json").exists() \
        and _PROGRAM_PATH.joinpath(sid).joinpath("service_meta").exists()


def create_sid_folder(sid: str):
    _PROGRAM_PATH.joinpath(sid).mkdir()


def delete_sid_folder(sid: str):
    shutil.rmtree(_PROGRAM_PATH.joinpath(sid))


def read_service_config(sid: str) -> dict:
    return json.loads(
        _PROGRAM_PATH.joinpath(sid).joinpath("config.json").read_text(
            encoding="utf8"))


def write_service_config(sid: str, config: dict):
    with open(_PROGRAM_PATH.joinpath(sid).joinpath("config.json"), "w") as f:
        json.dump(config, f)


def read_service_meta(sid: str) -> dict:
    return pickle.loads(
        _PROGRAM_PATH.joinpath(sid).joinpath("service_meta").read_bytes())


def write_service_meta(sid: str, meta: dict):
    with open(_PROGRAM_PATH.joinpath(sid).joinpath("service_meta"), "wb") as f:
        pickle.dump(meta, f)


def read_encrypted_database(sid: str) -> bytes:
    edb_bytes = _PROGRAM_PATH.joinpath(sid).joinpath("edb").read_bytes()
    return edb_bytes


def write_encrypted_database(sid: str, edb_bytes: bytes):
    with open(_PROGRAM_PATH.joinpath(sid).joinpath("edb"), "wb") as f:
        f.write(edb_bytes)


def delete_encrypted_database(sid: str):
    edb_path = _PROGRAM_PATH.joinpath(sid).joinpath("edb")
    edb_path.unlink(missing_ok=True)


def write_key(sid: str, key_bytes: bytes):
    with open(_PROGRAM_PATH.joinpath(sid).joinpath("key"), "wb") as f:
        f.write(key_bytes)


def read_key(sid: str) -> bytes:
    key_bytes = _PROGRAM_PATH.joinpath(sid).joinpath("key").read_bytes()
    return key_bytes
