import logging
import os
from os import path

from erdpy import config
from erdpy.testnet.config import TestnetConfiguration
from erdpy.testnet.nodes_setup_json import CHAIN_ID

chain_id = None
proxy = None

logger = logging.getLogger("scope")


def initialize():
    cwd = os.getcwd()
    testnet_toml = path.join(cwd, "testnet.toml")

    if os.path.exists(testnet_toml):
        global chain_id, proxy

        testnet_config = TestnetConfiguration.from_file(testnet_toml)
        chain_id = CHAIN_ID
        proxy = f"http://localhost:{testnet_config.proxy_port()}"


def get_chain_id():
    return chain_id or config.get_chain_id()


def get_tx_version() -> int:
    return config.get_tx_version()


def get_proxy() -> str:
    return proxy or config.get_proxy()
