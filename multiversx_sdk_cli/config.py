import os
from pathlib import Path
from typing import Any, Dict, List

import semver

from multiversx_sdk_cli import errors, utils

SDK_PATH = Path("~/multiversx-sdk").expanduser().resolve()
LOCAL_CONFIG_PATH = Path("mxpy.json").resolve()
GLOBAL_CONFIG_PATH = SDK_PATH / "mxpy.json"

DEFAULT_GAS_PRICE = 1000000000
GAS_PER_DATA_BYTE = 1500
MIN_GAS_LIMIT = 50000
MAX_GAS_LIMIT = 600000000


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
    default_value = get_defaults()[name]
    value = data.get(name, default_value)
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
        "proxy": "https://testnet-gateway.multiversx.com",
        "chainID": "T",
        "txVersion": "1",
        "dependencies.vmtools.tag": "latest",
        "dependencies.mx_sdk_rs.tag": "latest",
        "dependencies.vmtools.urlTemplate.linux": "https://github.com/multiversx/mx-chain-vm-go/archive/{TAG}.tar.gz",
        "dependencies.vmtools.urlTemplate.osx": "https://github.com/multiversx/mx-chain-vm-go/archive/{TAG}.tar.gz",
        "dependencies.llvm.tag": "v9-19feb",
        # ide.elrond.com will be removed, TBD if clang will still be downloaded
        "dependencies.llvm.urlTemplate.linux": "https://ide.elrond.com/vendor-llvm/{TAG}/linux-amd64.tar.gz?t=19feb",
        "dependencies.llvm.urlTemplate.osx": "https://ide.elrond.com/vendor-llvm/{TAG}/darwin-amd64.tar.gz?t=19feb",
        "dependencies.rust.tag": "nightly",
        "dependencies.nodejs.tag": "v12.18.3",
        "dependencies.nodejs.urlTemplate.linux": "https://nodejs.org/dist/{TAG}/node-{TAG}-linux-x64.tar.gz",
        "dependencies.nodejs.urlTemplate.osx": "https://nodejs.org/dist/{TAG}/node-{TAG}-darwin-x64.tar.gz",
        "dependencies.mx_chain_go.tag": "latest",
        "dependencies.mx_chain_go.urlTemplate.linux": "https://github.com/multiversx/mx-chain-go/archive/{TAG}.tar.gz",
        "dependencies.mx_chain_go.urlTemplate.osx": "https://github.com/multiversx/mx-chain-go/archive/{TAG}.tar.gz",
        "dependencies.mx_chain_go.url": "https://github.com/multiversx/mx-chain-go/archive/{TAG}.tar.gz",
        "dependencies.mx_chain_proxy_go.tag": "latest",
        "dependencies.mx_chain_proxy_go.urlTemplate.linux": "https://github.com/multiversx/mx-chain-proxy-go/archive/{TAG}.tar.gz",
        "dependencies.mx_chain_proxy_go.urlTemplate.osx": "https://github.com/multiversx/mx-chain-proxy-go/archive/{TAG}.tar.gz",
        "dependencies.golang.tag": "go1.18.4",
        "dependencies.golang.urlTemplate.linux": "https://golang.org/dl/{TAG}.linux-amd64.tar.gz",
        "dependencies.golang.urlTemplate.osx": "https://golang.org/dl/{TAG}.darwin-amd64.tar.gz",
        "dependencies.wasm-opt.tag": "latest",
        "dependencies.twiggy.tag": "latest",
        "dependencies.testwallets.tag": "latest",
        "dependencies.testwallets.urlTemplate.linux": "https://github.com/multiversx/mx-sdk-testwallets/archive/{TAG}.tar.gz",
        "dependencies.testwallets.urlTemplate.osx": "https://github.com/multiversx/mx-sdk-testwallets/archive/{TAG}.tar.gz",
        "testnet.validate_expected_keys": "false",
        "github_api_token": "",
    }


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
    extra_args = []
    for key, value in config_args.items():
        key_arg = f'--{key}'
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
    verbose_flag = '--verbose'
    pre_args = []
    if verbose_flag in extra_args:
        extra_args.remove(verbose_flag)
        pre_args = [verbose_flag]

    return pre_args + argv + extra_args


def get_dependency_directory(key: str, tag: str) -> Path:
    parent_directory = get_dependency_parent_directory(key)
    if tag == 'latest':
        tag = get_latest_semver_from_directory(parent_directory)

    return parent_directory / tag


def get_dependency_parent_directory(key: str) -> Path:
    return SDK_PATH / key


def get_latest_semver_from_directory(directory: Path) -> str:
    subdirs = [subdir.name for subdir in directory.iterdir()]
    try:
        return get_latest_semver(subdirs)
    except IndexError:
        raise Exception(f'no versions found in {directory}')


def get_latest_semver(versions: List[str]) -> str:
    semantic_versions = parse_strings_to_semver(versions)
    latest_version = sorted(semantic_versions).pop()
    return 'v' + str(latest_version)


def parse_strings_to_semver(version_strings: List[str]) -> List[semver.VersionInfo]:
    versions = []
    for version_string in version_strings:
        try:
            # Omit the 'v' prefix of the version string
            version_string = version_string[1:]
            version = semver.VersionInfo.parse(version_string)
        except ValueError:
            continue

        versions.append(version)

    return versions
