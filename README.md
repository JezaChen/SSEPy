# SSEPy: Implementation of searchable symmetric encryption in pure Python

![SSEPy Logo](https://s3.bmp.ovh/imgs/2022/03/885a91b23aff75d2.jpg)

Source Code: https://github.com/JezaChen/SSEPy

Searchable symmetric encryption, one of the research hotspots in applied cryptography, has continued to be studied for two decades. A number of excellent SSE schemes have emerged, enriching functionality and optimizing performance. However, many SSE schemes have not been implemented concretely and are generally stuck in the prototype implementation stage, and worse, most SSE schemes are not publicly available in source code. Based on this foundation, this project first implements SSE schemes (first single-keyword, then multi-keyword) published in top conferences and journals, and then implements them into concrete applications. I hope that this project will provide a good aid for researchers as well as a reference for industry.

This is a project that is moving forward...

## Usage

### Environment

- Python 3.8+
- OpenSSL
- libffi
- build-essential (for Debain), build-base (for Alpine)

### Install Required Packages
Before running, you need to install the necessary packages

```shell
pip3 install -r requirements.txt
```

### Adjust global configuration

The global configuration file is on global_config.py, 
which is divided into client-side global configuration and server-side global configuration.
The example files are as follows:

```python
import logging


# FOR CLIENT
class ClientConfig:
    SERVER_URI = "ws://localhost:8001"
    CONSOLE_LOG_LEVEL = logging.WARNING
    FILE_LOG_LEVEL = logging.INFO


# FOR SERVER
class ServerConfig:
    HOST = ""
    PORT = 8001
```

Among them, ClientConfig indicates the client configuration,
where `SERVER_URI` indicates the WebSocket address of the server, 
`CONSOLE_LOG_LEVEL` indicates the console log output level, 
and `FILE_LOG_LEVEL` indicates the file log output level;
`ServerConfig` indicates the server configuration, 
where `HOST` indicates the listening address, 
and `PORT` indicates the bound port.

### Server

The server just needs to run `run_server.py`

#### Run Server
```shell
 python3 run_server.py start
```

### Client

#### 1. Generate Config File

The CLI command `generate-config` generates a default configuration file 
by giving the SSE scheme name and 
configuration file output path. 
The user can then open the configuration file and modify it as needed.

- command: `generate-config`
- options:
  - `--scheme`: the name of the SSE scheme
  - `--save-path`: the path where the configuration file is saved
- example:
    ```
    python3 run_client.py generate-config --scheme CJJ14.PiBas --save-path cjj14_config

    >>> Create default config of CJJ14.PiBas successfully.
    ```
  
  The default configuration of the PiBas scheme is as follows:
  
  ```json
  {
    "scheme": "CJJ14.PiBas", 
    "param_lambda": 32, 
    "prf_f_output_length": 32,
    "prf_f": "HmacPRF",
    "ske": "AES-CBC"
  }
  ```

#### 2. According to the configuration, create an SSE service

Given a configuration file path, 
the client CLI command `create-service` creates a service 
and returns the service id (sid).

- command: `create-service`
- options:
  - `--config`: the file path of configuration
  - `--sname`: service name, an alias of service id
- returns: the sid of the created service
- example:
    ```
    python3 run_client.py create-service --config cjj14_config --sname pibas_s0

    >>> Create service e9cbf76d6578ba967f5a1d80250096f59a0524cea9c8a4d47f0bf92c157f1959 successfully.
    >>> sid: e9cbf76d6578ba967f5a1d80250096f59a0524cea9c8a4d47f0bf92c157f1959
    >>> sname: pibas_s0
    ```
    where `e9cbf76d6578ba967f5a1d80250096f59a0524cea9c8a4d47f0bf92c157f1959` is the service id


#### 3. Upload configuration file

After the configuration file is created, the user can use the `upload-config` command, 
enter the sid (service id) or sname (service name), and the CLI uploads the configuration file of the service to the server.

- command: `upload-config`
- options:
  - `--sid` or `--sname`: (choose one of two) the service id or service name
- example:
  ```
  python3 run_client.py upload-config --sname pibas_s0

  >>> Upload config successfully
  ```

#### 4. Create SSE Key

After the configuration file is created, the user can use the command `generate-key`, 
enter the sid or sname, and the CLI will generate the SSE key.

- command: `generate-key`
- options:
  - `--sid` or `--sname`: (choose one of two) the service id or service name
- example:
  ```
  python3 run_client.py generate-key --sname pibas_s0
  
  >>> Generate key successfully.
  ```

#### 5. Generate Encrypted Database

After creating the configuration file and key, the user can use the command `encrypt-database`, 
enter the sid (or sname) and database path, and the CLI will generate an encrypted database.

- command: `encrypt-database`
- options:
  - `--sid` or `--sname`: (choose one of two) the service id or service name
  - `--db-path`: the file path of database
- example:
  ```
  python3 run_client.py encrypt-database --sname pibas_s0 --db-path example_db.json
  
  >>> Encrypted Database successfully.
  ```

Currently, the database is a json file. 
Our project provides an example database example_db.json, the content is as follows.

```json
{
  "China": [
    "3A4B1ACC",
    "2DDD1FFF",
    "1122AA4B",
    "C2C2C2C2"
  ],
  "Github": [
    "1A1ADD2C",
    "2222CC1F"
  ],
  "Chen": [
    "1BB2BB2B",
    "23327878",
    "88771ABB"
  ]
}
```
The database consists of a dictionary where the keys are utf-8 strings 
and the values are an array whose elements are hex strings (don't start with `0x`).

#### 6. Upload Encrypted Database

After the database is created, the user can use the command `upload-encrypted-database`, 
enter the sid, and the CLI will upload the encrypted database to the server.

- command: `upload-encrypted-database`
- options:
  - `--sid` or `--sname`: (choose one of two) the service id or service name
- example:
  ```
  python3 run_client.py upload-encrypted-database --sname pibas_s0
  
  >>> Upload encrypted database successfully
  ```

#### 7. Keyword Search

After the encrypted database is uploaded, the user can use the `search` command, 
enter a keyword (currently only single-keyword search is supported) 
and the sid, encrypt it into a token and upload it to the server for searching.

- command: `search`
- options:
  - `--sid` or `--sname`: (choose one of two) the service id or service name
  - `--keyword`: the query keyword
- example:
  ```
  python3 run_client.py search --keyword Chen --sname pibas_s0
  
  >>> The result is [b'\x1b\xb2\xbb+', b'#2xx', b'\x88w\x1a\xbb'].
  ```

## Implemented schemes

### Single-keyword Static SSE Schemes

- (Completed) SSE-1 and SSE-2 in \[CGKO06\]: Curtmola, Reza, et al. "Searchable symmetric encryption: improved definitions and efficient constructions." Proceedings of the 13th ACM conference on Computer and communications security. 2006.
- (Completed) Schemes PiBas, PiPack, PiPtr and Pi2Lev in \[CJJ+14\]: Cash, David, et al. "Dynamic Searchable Encryption in Very-Large Databases: Data Structures and Implementation." (2014).
- (Completed) Scheme Pi in \[CT14\]: Cash, David, and Stefano Tessaro. "The locality of searchable symmetric encryption." Annual international conference on the theory and applications of cryptographic techniques. Springer, Berlin, Heidelberg, 2014.
- (Completed) Scheme 3 (Section 5, Construction 5.1) in \[ANSS16\]: Asharov, Gilad, et al. "Searchable symmetric encryption: optimal locality in linear space via two-dimensional balanced allocations." Proceedings of the forty-eighth annual ACM symposium on Theory of Computing. 2016.
- (Completed) Scheme in \[DP17\]: Demertzis, Ioannis, and Charalampos Papamanthou. "Fast searchable encryption with tunable locality." Proceedings of the 2017 ACM International Conference on Management of Data. 2017.
