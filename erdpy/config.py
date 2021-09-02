import os.path
from typing import Any, Dict

from erdpy import errors, utils

ROOT_FOLDER_NAME = "elrondsdk"
LOCAL_CONFIG_PATH = os.path.join(os.getcwd(), "erdpy.json")
CONFIG_PATH = os.path.expanduser("~/elrondsdk/erdpy.json")

DEFAULT_GAS_PRICE = 1000000000
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
    DELEGATION_MANAGER_OPS = 50000000
    DELEGATION_OPS = 1000000
    UNSTAKE_TOKENS = 5000000
    UNBOND_TOKENS = 5000000


def get_proxy() -> str:
    return get_value("proxy")


def get_chain_id() -> str:
    return get_value("chainID")


def get_tx_version() -> int:
    return int(get_value("txVersion"))


def get_dependency_tag(key: str) -> str:
    return get_value(f"dependencies.{key}.tag")


def set_dependency_tag(key: str, tag: str):
    set_value(f"dependencies.{key}.tag", tag)


def get_dependency_url(key: str, tag: str, platform: str) -> str:
    url_template = get_value(f"dependencies.{key}.urlTemplate.{platform}")
    return url_template.replace("{TAG}", tag)


def get_value(name: str) -> str:
    _guard_valid_name(name)
    data = get_active()
    value = data.get(name, get_defaults()[name])
    assert isinstance(value, str)
    return value


def set_value(name: str, value: Any):
    _guard_valid_name(name)
    data = read_file()
    active_config = data.get("active", "default")
    data.setdefault("configurations", {})
    data["configurations"].setdefault(active_config, {})
    data["configurations"][active_config][name] = value
    write_file(data)


def get_active():
    data = read_file()
    configs = data.get("configurations", {})
    active_config = data.get("active", "default")

    return configs.get(active_config, {})


def set_active(name: str):
    data = read_file()
    _guard_valid_config_name(data, name)
    data["active"] = name
    write_file(data)


def create_new_config(name: str, template: str):
    data = read_file()
    _guard_config_unique(data, name)
    new_config = {}
    if template is not None and template != "":
        _guard_valid_config_name(data, template)
        new_config = data["configurations"][template]

    data["active"] = name
    data.setdefault('configurations', {})
    data["configurations"][name] = new_config
    write_file(data)


def delete_config(name: str):
    _guard_valid_config_deletion(name)
    data = read_file()
    data["configurations"].pop(name, None)
    if data["active"] == name:
        data["active"] = "default"
    write_file(data)


def _guard_valid_name(name: str):
    if name not in get_defaults().keys():
        raise errors.UnknownConfigurationError(name)


def _guard_valid_config_name(config: Any, name: str):
    configurations = config.get('configurations', {})
    if name not in configurations:
        raise errors.UnknownConfigurationError(name)


def _guard_config_unique(config: Any, name: str):
    configurations = config.get('configurations', {})
    if name in configurations:
        raise errors.ConfigurationShouldBeUniqueError(name)


def _guard_valid_config_deletion(name: str):
    if name == "default":
        raise errors.ConfigurationProtectedError(name)


def get_defaults() -> Dict[str, Any]:
    return {
        "proxy": "https://testnet-gateway.elrond.com",
        "chainID": "T",
        "txVersion": "1",
        "dependencies.arwentools.tag": "v1.1.2",
        "dependencies.elrond_wasm_rs.tag": "v0.12.0",
        "dependencies.arwentools.urlTemplate.linux": "https://github.com/ElrondNetwork/arwen-wasm-vm/archive/{TAG}.tar.gz",
        "dependencies.arwentools.urlTemplate.osx": "https://github.com/ElrondNetwork/arwen-wasm-vm/archive/{TAG}.tar.gz",
        "dependencies.llvm.tag": "v9-19feb",
        "dependencies.llvm.urlTemplate.linux": "https://ide.elrond.com/vendor-llvm/{TAG}/linux-amd64.tar.gz?t=19feb",
        "dependencies.llvm.urlTemplate.osx": "https://ide.elrond.com/vendor-llvm/{TAG}/darwin-amd64.tar.gz?t=19feb",
        "dependencies.rust.tag": "",
        "dependencies.nodejs.tag": "v12.18.3",
        "dependencies.nodejs.urlTemplate.linux": "https://nodejs.org/dist/{TAG}/node-{TAG}-linux-x64.tar.gz",
        "dependencies.nodejs.urlTemplate.osx": "https://nodejs.org/dist/{TAG}/node-{TAG}-darwin-x64.tar.gz",
        "dependencies.elrond_go.tag": "master",
        "dependencies.elrond_go.urlTemplate.linux": "https://github.com/ElrondNetwork/elrond-go/archive/{TAG}.tar.gz",
        "dependencies.elrond_go.urlTemplate.osx": "https://github.com/ElrondNetwork/elrond-go/archive/{TAG}.tar.gz",
        "dependencies.elrond_go.url": "https://github.com/ElrondNetwork/elrond-go/archive/{TAG}.tar.gz",
        "dependencies.elrond_proxy_go.tag": "master",
        "dependencies.elrond_proxy_go.urlTemplate.linux": "https://github.com/ElrondNetwork/elrond-proxy-go/archive/{TAG}.tar.gz",
        "dependencies.elrond_proxy_go.urlTemplate.osx": "https://github.com/ElrondNetwork/elrond-proxy-go/archive/{TAG}.tar.gz",
        "dependencies.golang.tag": "go1.15.2",
        "dependencies.golang.urlTemplate.linux": "https://golang.org/dl/{TAG}.linux-amd64.tar.gz",
        "dependencies.golang.urlTemplate.osx": "https://golang.org/dl/{TAG}.darwin-amd64.tar.gz",
        "dependencies.mcl_signer.tag": "v1.0.0",
        "dependencies.mcl_signer.urlTemplate.linux": "https://github.com/ElrondNetwork/elrond-sdk-go-tools/releases/download/{TAG}/mcl_signer_{TAG}_ubuntu-latest.tar.gz",
        "dependencies.mcl_signer.urlTemplate.osx": "https://github.com/ElrondNetwork/elrond-sdk-go-tools/releases/download/{TAG}/mcl_signer_{TAG}_macos-latest.tar.gz",
    }


def read_file() -> Dict[str, Any]:
    if os.path.isfile(LOCAL_CONFIG_PATH):
        return utils.read_json_file(LOCAL_CONFIG_PATH)
    if os.path.isfile(CONFIG_PATH):
        return utils.read_json_file(CONFIG_PATH)
    return dict()


def write_file(data: Dict[str, Any]):
    if os.path.isfile(LOCAL_CONFIG_PATH):
        utils.write_json_file(LOCAL_CONFIG_PATH, data)
    else:
        utils.write_json_file(CONFIG_PATH, data)
