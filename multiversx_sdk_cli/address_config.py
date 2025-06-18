from functools import cache
from pathlib import Path
from typing import Any

from multiversx_sdk_cli.constants import SDK_PATH
from multiversx_sdk_cli.errors import (
    AliasAlreadyExistsError,
    AliasProtectedError,
    InvalidAddressConfigValue,
    UnknownAddressAliasError,
)
from multiversx_sdk_cli.utils import read_json_file, write_json_file

LOCAL_ADDRESS_CONFIG_PATH = Path("addresses.mxpy.json").resolve()
GLOBAL_ADDRESS_CONFIG_PATH = SDK_PATH / "addresses.mxpy.json"


def get_defaults() -> dict[str, str]:
    """
    Not all values are required for a config to be valid.

    Valid config for PEM wallets:
    ```
    {
        "kind": "pem",
        "path": "/path/to/wallet.pem",
        "index": "0"  # optional, defaults to 0
    }
    ```

    Valid config for KEYSTORE wallets:
    ```
    {
        "kind": "keystore",
        "path": "/path/to/wallet.json",
        "index": "0"  # optional, defaults to 0
    }
    ```

    For keystore wallets, you'll be prompted to enter the password when using the wallet.
    """
    return {
        "kind": "",
        "path": "",
        "index": "",
    }


@cache
def get_value(name: str) -> str:
    _guard_valid_name(name)
    data = get_active_address()
    default_value = get_defaults()[name]
    value = data.get(name, default_value)
    assert isinstance(value, str)
    return value


def _guard_valid_name(name: str):
    if name not in get_defaults().keys():
        raise InvalidAddressConfigValue(f"Key is not present in address config: [{name}]")


def get_active_address() -> dict[str, str]:
    """Returns the active address configuration."""
    data = read_address_config_file()
    addresses: dict[str, Any] = data.get("addresses", {})
    active_address: str = data.get("active", "default")
    result: dict[str, str] = addresses.get(active_address, {})

    return result


@cache
def read_address_config_file() -> dict[str, Any]:
    config_path = resolve_address_config_path()
    if config_path.exists():
        data: dict[str, Any] = read_json_file(config_path)
        return data
    return dict()


def resolve_address_config_path() -> Path:
    if LOCAL_ADDRESS_CONFIG_PATH.is_file():
        return LOCAL_ADDRESS_CONFIG_PATH
    return GLOBAL_ADDRESS_CONFIG_PATH


def set_value(name: str, value: Any):
    """Sets a key-value pair in the active address config."""
    _guard_valid_name(name)
    data = read_address_config_file()
    active_env = data.get("active", "default")
    data.setdefault("addresses", {})
    data["addresses"].setdefault(active_env, {})
    data["addresses"][active_env][name] = value
    _write_file(data)


def _write_file(data: dict[str, Any]):
    env_path = resolve_address_config_path()
    write_json_file(str(env_path), data)


def set_active(name: str):
    """Switches to the address configuration with the given name."""
    data = read_address_config_file()
    _guard_valid_address_name(data, name)
    data["active"] = name
    _write_file(data)


def _guard_valid_address_name(env: Any, name: str):
    envs = env.get("addresses", {})
    if name not in envs:
        raise UnknownAddressAliasError(name)


def create_new_address_config(name: str, template: str):
    """Creates a new address config with the given name and optional template."""
    data = read_address_config_file()
    _guard_alias_unique(data, name)
    new_address = {}
    if template:
        _guard_valid_address_name(data, template)
        new_address = data["addresses"][template]

    data["active"] = name
    data.setdefault("addresses", {})
    data["addresses"][name] = new_address
    _write_file(data)


def _guard_alias_unique(env: Any, name: str):
    envs = env.get("addresses", {})
    if name in envs:
        raise AliasAlreadyExistsError(name)


def delete_config_value(name: str):
    """Deletes a key-value pair of the active address config."""
    _guard_valid_alias_deletion(name)
    data = read_address_config_file()
    active_env = data.get("active", "default")
    data.setdefault("addresses", {})
    data["addresses"].setdefault(active_env, {})
    del data["addresses"][active_env][name]
    _write_file(data)


def delete_alias(name: str):
    """Deletes the address configuration with the given name."""
    _guard_valid_alias_deletion(name)
    data = read_address_config_file()
    data["addresses"].pop(name, None)
    if data["active"] == name:
        data["active"] = "default"
    _write_file(data)


def _guard_valid_alias_deletion(name: str):
    if name == "default":
        raise AliasProtectedError(name)
