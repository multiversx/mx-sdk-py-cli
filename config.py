import os.path

from erdpy import utils, errors


DOWNLOAD_MIRROR = "https://ide.elrond.com"
MODULES_CONFIG_URL = "https://raw.githubusercontent.com/ElrondNetwork/elrond-sdk/master/deps.json"
WITH_CHAIN_ID_AND_TX_VERSION = False

ROOT_FOLDER_NAME = "elrondsdk"
CONFIG_PATH = os.path.expanduser("~/elrondsdk/erdpy.json")

DEFAULT_GAS_PRICE = 200000000000
GAS_PER_DATA_BYTE = 1500
MIN_GAS_LIMIT = 50000


class MetaChainSystemSCsCost:
    STAKE = 5000000
    UNSTAKE = 5000000
    UNBOND = 5000000
    CLAIM = 5000000
    GET = 5000000
    CHANGE_REWARD_ADDRESS = 5000000
    CHANGE_VALIDATOR_KEYS = 5000000
    UNJAIL = 5000000


def get_chain_id() -> str:
    return get_value("chainID")


def get_tx_version() -> str:
    return get_value("txVersion")


def get_value(name) -> str:
    _guard_valid_name(name)
    data = _read_file()
    return data.get(name, get_defaults()[name])


def set_value(name, value):
    _guard_valid_name(name)
    data = _read_file()
    data[name] = value
    _write_file(data)


def _guard_valid_name(name):
    if name not in get_defaults().keys():
        raise errors.UnknownConfigurationError(name)


def get_defaults() -> dict:
    return {
        "proxy": "https://api.elrond.com",
        "chainID": "Testnet",
        "txVersion": "1"
    }


def _read_file() -> dict:
    if not os.path.isfile(CONFIG_PATH):
        return dict()
    return utils.read_json_file(CONFIG_PATH)


def _write_file(data: dict) -> dict:
    utils.write_json_file(CONFIG_PATH, data)
