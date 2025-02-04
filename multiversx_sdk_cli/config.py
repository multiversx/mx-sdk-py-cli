import os
from pathlib import Path
from typing import Any, Dict, List

from multiversx_sdk import NetworkProviderConfig

from multiversx_sdk_cli import errors, utils

SDK_PATH = Path("~/multiversx-sdk").expanduser().resolve()
LOCAL_CONFIG_PATH = Path("mxpy.json").resolve()
GLOBAL_CONFIG_PATH = SDK_PATH / "mxpy.json"


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


def get_dependency_resolution(key: str) -> str:
    try:
        return get_value(f"dependencies.{key}.resolution")
    except Exception:
        return ""


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
    default_value = get_defaults()[name]
    value = data.get(name, default_value)
    assert isinstance(value, str)
    return value


def get_address_hrp():
    return get_value("default_address_hrp")


def set_value(name: str, value: Any):
    _guard_valid_name(name)
    data = read_file()
    active_config = data.get("active", "default")
    data.setdefault("configurations", {})
    data["configurations"].setdefault(active_config, {})
    data["configurations"][active_config][name] = value
    write_file(data)


def delete_value(name: str):
    _guard_valid_config_deletion(name)
    data = read_file()
    active_config = data.get("active", "default")
    data.setdefault("configurations", {})
    data["configurations"].setdefault(active_config, {})
    del data["configurations"][active_config][name]
    write_file(data)


def get_active() -> Dict[str, Any]:
    data = read_file()
    configs = data.get("configurations", {})
    active_config_name: str = data.get("active", "default")
    empty_config: Dict[str, Any] = dict()
    result: Dict[str, Any] = configs.get(active_config_name, empty_config)

    return result


def set_active(name: str):
    data = read_file()
    _guard_valid_config_name(data, name)
    data["active"] = name
    write_file(data)


def create_new_config(name: str, template: str):
    data = read_file()
    _guard_config_unique(data, name)
    new_config = {}
    if template:
        _guard_valid_config_name(data, template)
        new_config = data["configurations"][template]

    data["active"] = name
    data.setdefault("configurations", {})
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
    configurations = config.get("configurations", {})
    if name not in configurations:
        raise errors.UnknownConfigurationError(name)


def _guard_config_unique(config: Any, name: str):
    configurations = config.get("configurations", {})
    if name in configurations:
        raise errors.ConfigurationShouldBeUniqueError(name)


def _guard_valid_config_deletion(name: str):
    if name == "default":
        raise errors.ConfigurationProtectedError(name)


def get_defaults() -> Dict[str, Any]:
    return {
        "dependencies.vmtools.tag": "v1.5.24",
        "dependencies.vmtools.urlTemplate.linux": "https://github.com/multiversx/mx-chain-vm-go/archive/{TAG}.tar.gz",
        "dependencies.vmtools.urlTemplate.osx": "https://github.com/multiversx/mx-chain-vm-go/archive/{TAG}.tar.gz",
        "dependencies.vmtools.urlTemplate.windows": "https://github.com/multiversx/mx-chain-vm-go/archive/{TAG}.tar.gz",
        "dependencies.rust.tag": "stable",
        "dependencies.golang.resolution": "SDK",
        "dependencies.golang.tag": "go1.20.7",
        "dependencies.golang.urlTemplate.linux": "https://golang.org/dl/{TAG}.linux-amd64.tar.gz",
        "dependencies.golang.urlTemplate.osx": "https://golang.org/dl/{TAG}.darwin-amd64.tar.gz",
        "dependencies.golang.urlTemplate.windows": "https://golang.org/dl/{TAG}.windows-amd64.zip",
        "dependencies.twiggy.tag": "",
        "dependencies.sc-meta.tag": "",
        "dependencies.testwallets.tag": "v1.0.0",
        "dependencies.testwallets.urlTemplate.linux": "https://github.com/multiversx/mx-sdk-testwallets/archive/{TAG}.tar.gz",
        "dependencies.testwallets.urlTemplate.osx": "https://github.com/multiversx/mx-sdk-testwallets/archive/{TAG}.tar.gz",
        "dependencies.testwallets.urlTemplate.windows": "https://github.com/multiversx/mx-sdk-testwallets/archive/{TAG}.tar.gz",
        "dependencies.wasm-opt.tag": "0.112.0",
        "github_api_token": "",
        "default_address_hrp": "erd",
    }


def get_deprecated_entries_in_config_file():
    default_config_keys = set(get_defaults().keys())
    current_config_keys = set(get_active().keys())
    return current_config_keys - default_config_keys


def resolve_config_path() -> Path:
    if os.path.isfile(LOCAL_CONFIG_PATH):
        return LOCAL_CONFIG_PATH
    return GLOBAL_CONFIG_PATH


def read_file() -> Dict[str, Any]:
    config_path = resolve_config_path()
    if config_path.exists():
        data: Dict[str, Any] = utils.read_json_file(config_path)
        return data
    return dict()


def write_file(data: Dict[str, Any]):
    config_path = resolve_config_path()
    utils.write_json_file(str(config_path), data)


def add_config_args(argv: List[str]) -> List[str]:
    try:
        command, subcommand, *_ = argv
    except ValueError:
        return argv

    config = read_file()

    try:
        config_args = config[command][subcommand]
    except KeyError:
        return argv

    final_args = determine_final_args(argv, config_args)
    print(f"Found extra arguments in mxpy.json. Final arguments: {final_args}")
    return final_args


def determine_final_args(argv: List[str], config_args: Dict[str, Any]) -> List[str]:
    extra_args: List[str] = []
    for key, value in config_args.items():
        key_arg = f"--{key}"
        # arguments from the command line override the config
        if key_arg in argv:
            continue
        if any(arg.startswith(f"{key_arg}=") for arg in argv):
            continue
        extra_args.append(key_arg)
        if value is True:
            continue
        if isinstance(value, List):
            for item in value:
                extra_args.append(str(item))
        else:
            extra_args.append(str(value))

    # the verbose flag is an exception since it has to go before the command and subcommand
    # eg. mxpy --verbose contract deploy
    verbose_flag = "--verbose"
    pre_args = []
    if verbose_flag in extra_args:
        extra_args.remove(verbose_flag)
        pre_args = [verbose_flag]

    return pre_args + argv + extra_args


def get_dependency_directory(key: str, tag: str) -> Path:
    parent_directory = get_dependency_parent_directory(key)
    return parent_directory / tag


def get_dependency_parent_directory(key: str) -> Path:
    return SDK_PATH / key


def get_config_for_network_providers() -> NetworkProviderConfig:
    return NetworkProviderConfig(client_name="mxpy")
