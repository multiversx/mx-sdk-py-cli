from functools import cache
from pathlib import Path
from typing import Any, Optional

from multiversx_sdk_cli.constants import SDK_PATH
from multiversx_sdk_cli.errors import (
    AliasAlreadyExistsError,
    AliasProtectedError,
    InvalidAddressConfigValue,
    UnknownWalletAliasError,
)
from multiversx_sdk_cli.utils import read_json_file, write_json_file

LOCAL_WALLET_CONFIG_PATH = Path("wallets.mxpy.json").resolve()
GLOBAL_WALLET_CONFIG_PATH = SDK_PATH / "wallets.mxpy.json"


def get_defaults() -> dict[str, str]:
    """
    Not all values are required for a config to be valid.

    Valid config for PEM wallets:
    ```
    {
        "path": "/path/to/wallet.pem",
        "index": "0"  # optional, defaults to 0
    }
    ```

    Valid config for KEYSTORE wallets:
    ```
    {
        "path": "/path/to/wallet.json",
        "index": "0"  # optional, defaults to 0
    }
    ```

    For keystore wallets, you'll be prompted to enter the password when using the wallet.
    """
    return {
        "path": "",
        "index": "0",
    }


@cache
def get_value(name: str, alias: str) -> str:
    _guard_valid_name(name)
    data = read_wallet_config_file()
    available_wallets = data.get("wallets", {})

    wallet = available_wallets.get(alias, None)
    if wallet is None:
        raise UnknownWalletAliasError(alias)

    default_value = get_defaults()[name]
    value = wallet.get(name, default_value)
    assert isinstance(value, str)
    return value


def _guard_valid_name(name: str):
    if name not in get_defaults().keys():
        raise InvalidAddressConfigValue(f"Key is not present in wallet config: [{name}]")


def get_active_wallet() -> dict[str, str]:
    """Returns the active wallet configuration."""
    data = read_wallet_config_file()
    addresses: dict[str, Any] = data.get("wallets", {})
    active_address: str = data.get("active", "default")
    result: dict[str, str] = addresses.get(active_address, {})

    return result


@cache
def read_wallet_config_file() -> dict[str, Any]:
    config_path = resolve_wallet_config_path()
    if config_path.exists():
        data: dict[str, Any] = read_json_file(config_path)
        return data
    return dict()


def resolve_wallet_config_path() -> Path:
    if LOCAL_WALLET_CONFIG_PATH.is_file():
        return LOCAL_WALLET_CONFIG_PATH
    return GLOBAL_WALLET_CONFIG_PATH


def set_value(name: str, value: str, alias: str):
    """Sets a key-value pair in the specified wallet config."""
    _guard_valid_name(name)
    data = read_wallet_config_file()
    available_wallets = data.get("wallets", {})

    wallet = available_wallets.get(alias, None)
    if wallet is None:
        raise UnknownWalletAliasError(alias)

    wallet[name] = value
    available_wallets[alias] = wallet
    data["wallets"] = available_wallets
    _write_file(data)


def _write_file(data: dict[str, Any]):
    env_path = resolve_wallet_config_path()
    write_json_file(str(env_path), data)


def switch_wallet(name: str):
    """Switches to the wallet configuration with the given name."""
    data = read_wallet_config_file()
    _guard_valid_wallet_name(data, name)
    data["active"] = name
    _write_file(data)


def _guard_valid_wallet_name(env: Any, name: str):
    envs = env.get("wallets", {})
    if name not in envs:
        raise UnknownWalletAliasError(name)


def create_new_wallet_config(name: str, path: Optional[str] = None):
    """Creates a new wallet config with the given name and sets it as the default wallet."""
    data = read_wallet_config_file()
    _guard_alias_unique(data, name)
    new_wallet = {}

    if path:
        new_wallet["path"] = path

    data["active"] = name
    data.setdefault("wallets", {})
    data["wallets"][name] = new_wallet
    _write_file(data)


def _guard_alias_unique(env: Any, name: str):
    wallets = env.get("wallets", {})
    if name in wallets:
        raise AliasAlreadyExistsError(name)


def delete_config_value(key: str, alias: str):
    """Deletes a key-value pair of the specified wallet config."""
    _guard_valid_name(key)

    data = read_wallet_config_file()
    available_wallets = data.get("wallets", {})

    wallet = available_wallets.get(alias, None)
    if wallet is None:
        raise UnknownWalletAliasError(alias)

    del wallet[key]
    available_wallets[alias] = wallet
    data["wallets"] = available_wallets
    _write_file(data)


def delete_alias(name: str):
    """Deletes the wallet configuration with the given name."""
    _guard_valid_alias_deletion(name)
    data = read_wallet_config_file()
    data["wallets"].pop(name, None)
    if data["active"] == name:
        data["active"] = "default"
    _write_file(data)


def _guard_valid_alias_deletion(name: str):
    if name == "default":
        raise AliasProtectedError(name)
