import os.path

from typing import Any, Dict
from erdpy import errors, utils

MODULES_CONFIG_URL = "https://raw.githubusercontent.com/ElrondNetwork/elrond-sdk/master/deps.json"

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


def get_proxy() -> str:
    return get_value("proxy")


def get_chain_id() -> str:
    return get_value("chainID")


def get_tx_version() -> int:
    return int(get_value("txVersion"))


def get_with_chain_and_version() -> bool:
    return utils.str_to_bool(get_value("withChainAndVersion"))


def get_dependency_tag(key: str) -> str:
    return get_value(f"dependencies.{key}.tag")


def set_dependency_tag(key: str, tag: str):
    set_value(f"dependencies.{key}.tag", tag)


def get_dependency_url(key: str, tag: str, platform: str) -> str:
    url_template = get_value(f"dependencies.{key}.urlTemplate.{platform}")
    return url_template.replace("{TAG}", tag)


def get_value(name: str) -> str:
    _guard_valid_name(name)
    data = read_file()
    return data.get(name, get_defaults()[name])


def set_value(name: str, value: Any):
    _guard_valid_name(name)
    data = read_file()
    data[name] = value
    write_file(data)


def _guard_valid_name(name: str):
    if name not in get_defaults().keys():
        raise errors.UnknownConfigurationError(name)


def get_defaults() -> Dict[str, Any]:
    return {
        "proxy": "https://api.elrond.com",
        "chainID": "Testnet",
        "txVersion": "1",
        "withChainAndVersion": False,
        "dependencies.arwentools.tag": "v0.3.26-12-g466a26b",
        "dependencies.arwentools.urlTemplate.linux": "https://ide.elrond.com/travis-builds/ARWEN_{TAG}_linux_amd64.tar.gz",
        "dependencies.arwentools.urlTemplate.osx": "https://ide.elrond.com/travis-builds/ARWEN_{TAG}_darwin_amd64.tar.gz",
        "dependencies.llvm.tag": "v9-19feb",
        "dependencies.llvm.urlTemplate.linux": "https://ide.elrond.com/vendor-llvm/{TAG}/linux-amd64.tar.gz?t=19feb",
        "dependencies.llvm.urlTemplate.osx": "https://ide.elrond.com/vendor-llvm/{TAG}/darwin-amd64.tar.gz?t=19feb",
        "dependencies.rust.tag": "",
    }


def read_file() -> Dict[str, Any]:
    if not os.path.isfile(CONFIG_PATH):
        return dict()
    return utils.read_json_file(CONFIG_PATH)


def write_file(data: Dict[str, Any]):
    utils.write_json_file(CONFIG_PATH, data)
