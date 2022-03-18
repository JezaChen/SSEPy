# -*- coding:utf-8 _*-
""" 
LIB-SSE CODE
@author: Jeza Chen
@license: GPL-3.0 License
@file: run_client.py 
@time: 2022/03/18
@contact: jeza@vip.qq.com
@site:  
@software: PyCharm 
@description: 
"""

import asyncclick as click

import frontend.client.commands as client_commands


@click.group()
async def cli():
    pass


@cli.command()
@click.option("--scheme", help='name of SSE scheme')
@click.option("--save-path", help='save file path')
async def generate_config(scheme, save_path):
    if scheme is None or save_path is None:
        click.echo(f'Incomplete options')
        return
    client_commands.generate_default_config(scheme, save_path)


@cli.command()
@click.option("--config", help='file path of config')
async def create_service(config):
    if config is None:
        click.echo(f'Incomplete options')
        return

    client_commands.create_service(config_path=config)


@cli.command()
@click.option("--sid", help='service id')
async def upload_config(sid):
    if sid is None:
        click.echo(f'Incomplete options')
        return

    await client_commands.upload_config(sid)


@cli.command()
@click.option("--sid", help='service id')
async def generate_key(sid):
    if sid is None:
        click.echo(f'Incomplete options')
        return

    client_commands.generate_key(sid)


@cli.command()
@click.option("--sid", help='service id')
@click.option("--db-path", help='database path')
async def encrypt_database(sid, db_path):
    if sid is None or db_path is None:
        click.echo(f'Incomplete options')
        return

    client_commands.encrypt_database(sid, db_path)


@cli.command()
@click.option("--sid", help='service id')
async def upload_encrypted_database(sid):
    if sid is None:
        click.echo(f'Incomplete options')
    await client_commands.upload_encrypted_database(sid)


@cli.command()
@click.option("--sid", help='service id')
@click.option("--keyword", help='keyword to search')
async def search(sid, keyword):
    if sid is None or keyword is None:
        click.echo(f'Incomplete options')
        return

    await client_commands.search(sid, keyword)


if __name__ == '__main__':
    cli(_anyio_backend="asyncio")
