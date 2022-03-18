# SSEPy: Implementation of searchable symmetric encryption in pure Python

Searchable symmetric encryption, one of the research hotspots in applied cryptography, has continued to be studied for two decades. A number of excellent SSE schemes have emerged, enriching functionality and optimizing performance. However, many SSE schemes have not been implemented concretely and are generally stuck in the prototype implementation stage, and worse, most SSE schemes are not publicly available in source code. Based on this foundation, this project first implements SSE schemes (first single-keyword, then multi-keyword) published in top conferences and journals, and then implements them into concrete applications. I hope that this project will provide a good aid for researchers as well as a reference for industry.

This is a project that is moving forward...

## Usage

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

#### Generate Config File

The CLI command `generate-config` generates a default configuration file 
by giving the SSE scheme name and 
configuration file output path. 
The user can then open the configuration file and modify it as needed.

```shell
python3 run_client.py generate-config --scheme CJJ14.PiBas --save-path cjj14_config
```

It returns:

```
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

#### According to the configuration, create an SSE service

Given a configuration file path, 
the client CLI command `create-service` creates a service 
and returns the service id (sid).

```shell
python3 run_client.py create-service --config cjj14_config 
```

It returns:

```
>>> Create service bd1f9ce64409b6c4ba0d5ac4550ed948716e18dc2ea2318ab486877192fc93fe successfully.
```

, where `bd1f9ce64409b6c4ba0d5ac4550ed948716e18dc2ea2318ab486877192fc93fe` is the service id.


#### Upload configuration file

After the configuration file is created, the user can use the `upload-config` command, 
enter the sid, and the CLI uploads the configuration file of the service to the server.

```shell
python3 run_client.py upload-config --sid bd1f9ce64409b6c4ba0d5ac4550ed948716e18dc2ea2318ab486877192fc93fe
```

The CLI returns 

```
>>> Upload config successfully
```

#### Create SSE Key

After the configuration file is created, the user can use the command `generate-key`, 
enter the sid, and the CLI will generate the SSE key.

```shell
python3 run_client.py generate-key --sid bd1f9ce64409b6c4ba0d5ac4550ed948716e18dc2ea2318ab486877192fc93fe
```

The CLI returns

```
>>> Generate key successfully.
```

#### Generate Encrypted Database

After creating the configuration file and key, the user can use the command encrypt-database, 
enter the sid and database path, and the CLI will generate an encrypted database.

```shell
python3 run_client.py encrypt-database --sid bd1f9ce64409b6c4ba0d5ac4550ed948716e18dc2ea2318ab486877192fc93fe --db-path example_db.json
```

The CLI returns

```
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

#### Upload Encrypted Database

After the database is created, the user can use the command `upload-encrypted-database`, 
enter the sid, and the CLI will upload the encrypted database to the server.

```shell
python3 run_client.py upload-encrypted-database --sid bd1f9ce64409b6c4ba0d5ac4550ed948716e18dc2ea2318ab486877192fc93fe
```

The CLI returns

```
>>> Upload encrypted database successfully
```

#### Keyword Search

After the encrypted database is uploaded, the user can use the search command, 
enter a keyword (currently only single-keyword search is supported) 
and the sid, encrypt it into a token and upload it to the server for searching.

```shell
python3 run_client.py search --keyword Chen --sid bd1f9ce64409b6c4ba0d5ac4550ed948716e18dc2ea2318ab486877192fc93fe
```

The CLI returns

```
>>> The result is [b'\x1b\xb2\xbb+', b'#2xx', b'\x88w\x1a\xbb'].
```

## Implemented schemes

### Single-keyword Static SSE Schemes

- (Completed) SSE-1 and SSE-2 in \[CGKO06\]: Curtmola, Reza, et al. "Searchable symmetric encryption: improved definitions and efficient constructions." Proceedings of the 13th ACM conference on Computer and communications security. 2006.
- (Completed) Schemes PiBas, PiPack, PiPtr and Pi2Lev in \[CJJ+14\]: Cash, David, et al. "Dynamic Searchable Encryption in Very-Large Databases: Data Structures and Implementation." (2014).
- (Completed) Scheme Pi in \[CT14\]: Cash, David, and Stefano Tessaro. "The locality of searchable symmetric encryption." Annual international conference on the theory and applications of cryptographic techniques. Springer, Berlin, Heidelberg, 2014.
- (Completed) Scheme 3 (Section 5, Construction 5.1) in \[ANSS16\]: Asharov, Gilad, et al. "Searchable symmetric encryption: optimal locality in linear space via two-dimensional balanced allocations." Proceedings of the forty-eighth annual ACM symposium on Theory of Computing. 2016.
