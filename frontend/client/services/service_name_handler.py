# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: service_name_handler.py
@time: 2022/03/23
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description:
Since the length of the sid is too long,
making the sid not easy to be remembered,
each service should have an alias (service name) to make it easy for people to remember.

The module records the mapping of service alias to sid
and handles the corresponding configuration reads and writes.
"""
import json
import pathlib
from typing import Optional, Dict, Any

_PROGRAM_DIR_PATH = pathlib.Path.home().joinpath(".sse/client/")
SERVICE_MAPPING_PATH = pathlib.Path(_PROGRAM_DIR_PATH).joinpath("service_mapping.json")


def _get_service_mapping_read_and_write_function():
    __service_name_mapping = None

    def _read_service_mapping() -> Optional[Dict[Any, Any]]:
        nonlocal __service_name_mapping

        if __service_name_mapping is not None:
            return __service_name_mapping
        try:
            with open(SERVICE_MAPPING_PATH) as f:
                __service_name_mapping = json.load(f)
                return __service_name_mapping
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {}

    def _write_service_mapping(new_mapping: dict):
        nonlocal __service_name_mapping
        __service_name_mapping = new_mapping
        if not _PROGRAM_DIR_PATH.exists():
            _PROGRAM_DIR_PATH.mkdir(parents=True)

        with open(SERVICE_MAPPING_PATH, "w") as f:
            json.dump(new_mapping, f)

    return _read_service_mapping, _write_service_mapping


read_service_mapping, write_service_mapping = _get_service_mapping_read_and_write_function()


def get_service_id_by_sname(sname: str) -> str:
    mapping = read_service_mapping()
    try:
        return mapping[sname]
    except KeyError:
        raise KeyError(f"The service id corresponding to sname {sname} not found.")


def record_sname_id_pair(sname: str, sid: str):
    mapping = read_service_mapping()
    if sname in mapping:
        raise KeyError(f"The service name {sname} already exists.")
    mapping[sname] = sid
    write_service_mapping(mapping)
