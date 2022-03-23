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
@click.option("--sname", help='service name')
async def create_service(config, sname):
    if config is None:
        click.echo(f'Incomplete options')
        return

    client_commands.create_service(config_path=config, sname=sname)


@cli.command()
@click.option("--sid", help='service id', default='')
@click.option("--sname", help='service name', dafault='')
async def upload_config(sid, sname):
    if not sid and not sname:
        click.echo(f'One of the two options --sid or --sname must be assigned')
        return

    await client_commands.upload_config(sid=sid, sname=sname)


@cli.command()
@click.option("--sid", help='service id', default='')
@click.option("--sname", help='service name', dafault='')
async def generate_key(sid, sname):
    if not sid and not sname:
        click.echo(f'One of the two options --sid or --sname must be assigned')
        return

    client_commands.generate_key(sid=sid, sname=sname)


@cli.command()
@click.option("--sid", help='service id', default='')
@click.option("--sname", help='service name', dafault='')
@click.option("--db-path", help='database path')
async def encrypt_database(sid, sname, db_path):
    if db_path is None:
        click.echo(f'Incomplete options: --db-path')
        return

    if not sid and not sname:
        click.echo(f'One of the two options --sid or --sname must be assigned')
        return

    client_commands.encrypt_database(db_path, sid=sid, sname=sname)


@cli.command()
@click.option("--sid", help='service id', default='')
@click.option("--sname", help='service name', dafault='')
async def upload_encrypted_database(sid, sname):
    if not sid and not sname:
        click.echo(f'One of the two options --sid or --sname must be assigned')
        return
    await client_commands.upload_encrypted_database(sid=sid, sname=sname)


@cli.command()
@click.option("--sid", help='service id', default='')
@click.option("--sname", help='service name', dafault='')
@click.option("--keyword", help='keyword to search')
@click.option("--output-format",
              help='Specify the output format, which currently supports '
                   'int, hex, raw and utf8, where utf8 format output must require that'
                   ' the byte string of the file identifier must be converted from a utf8 string',
              default="raw")
async def search(sid, sname, keyword, output_format):
    if keyword is None:
        click.echo(f'Incomplete options: --keyword')
        return
    if not sid and not sname:
        click.echo(f'One of the two options --sid or --sname must be assigned')
        return

    await client_commands.search(keyword, output_format, sid=sid, sname=sname)


if __name__ == '__main__':
    cli(_anyio_backend="asyncio")
