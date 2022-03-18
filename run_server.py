# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: run_server.py 
@time: 2022/03/18
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""
import asyncclick as click

import frontend.server.connector
from global_config import ServerConfig


@click.group()
async def cli():
    pass


@cli.command()
@click.option("--host", default=ServerConfig.HOST, help='server host')
@click.option("--port",
              default=ServerConfig.PORT,
              help='port to bind',
              type=int)
async def start(host, port):
    if host is None or port is None:
        click.echo(f'Incomplete options')
    await frontend.server.connector.run_server(host, port)


if __name__ == '__main__':
    cli(_anyio_backend="asyncio")
