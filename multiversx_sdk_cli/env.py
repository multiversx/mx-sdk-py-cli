from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

from multiversx_sdk_cli.errors import (
    EnvironmentAlreadyExistsError,
    EnvironmentProtectedError,
    InvalidConfirmationSettingError,
    InvalidEnvironmentValue,
    UnknownEnvironmentError,
)
from multiversx_sdk_cli.utils import read_json_file, write_json_file

SDK_PATH = Path("~/multiversx-sdk").expanduser().resolve()
LOCAL_ENV_PATH = Path("env.mxpy.json").resolve()
GLOBAL_ENV_PATH = SDK_PATH / "env.mxpy.json"


@dataclass
class MxpyEnv:
    address_hrp: str
    proxy_url: str
    explorer_url: str
    ask_confirmation: bool

    @classmethod
    @cache
    def from_active_env(cls) -> "MxpyEnv":
        return cls(
            address_hrp=get_address_hrp(),
            proxy_url=get_proxy_url(),
            explorer_url=get_explorer_url(),
            ask_confirmation=get_confirmation_setting(),
        )


def get_defaults() -> dict[str, str]:
    return {
        "default_address_hrp": "erd",
        "proxy_url": "",
        "explorer_url": "",
        "ask_confirmation": "false",
    }


@cache
def get_address_hrp() -> str:
    return get_value("default_address_hrp")


@cache
def get_proxy_url() -> str:
    return get_value("proxy_url")


@cache
def get_explorer_url() -> str:
    return get_value("explorer_url")


@cache
def get_confirmation_setting() -> bool:
    confirmation_value = get_value("ask_confirmation")
    if confirmation_value.lower() in ["true", "yes", "1"]:
        return True
    elif confirmation_value.lower() in ["false", "no", "0"]:
        return False
    else:
        raise InvalidConfirmationSettingError(confirmation_value)


@cache
def get_value(name: str) -> str:
    _guard_valid_name(name)
    data = get_active_env()
    default_value = get_defaults()[name]
    value = data.get(name, default_value)
    assert isinstance(value, str)
    return value


def _guard_valid_name(name: str):
    if name not in get_defaults().keys():
        raise InvalidEnvironmentValue(f"Key is not present in environment config: [{name}]")


def get_active_env() -> dict[str, str]:
    data = read_env_file()
    envs: dict[str, Any] = data.get("environments", {})
    active_env_name: str = data.get("active", "default")
    result: dict[str, str] = envs.get(active_env_name, {})

    return result


@cache
def read_env_file() -> dict[str, Any]:
    env_path = resolve_env_path()
    if env_path.exists():
        data: dict[str, Any] = read_json_file(env_path)
        return data
    return dict()


def resolve_env_path() -> Path:
    if LOCAL_ENV_PATH.is_file():
        return LOCAL_ENV_PATH
    return GLOBAL_ENV_PATH


def set_value(name: str, value: Any):
    _guard_valid_name(name)
    data = read_env_file()
    active_env = data.get("active", "default")
    data.setdefault("environments", {})
    data["environments"].setdefault(active_env, {})
    data["environments"][active_env][name] = value
    write_file(data)


def write_file(data: dict[str, Any]):
    env_path = resolve_env_path()
    write_json_file(str(env_path), data)


def delete_value(name: str):
    """Deletes a key-value pair of the active env."""
    _guard_valid_env_deletion(name)
    data = read_env_file()
    active_env = data.get("active", "default")
    data.setdefault("environments", {})
    data["environments"].setdefault(active_env, {})
    del data["environments"][active_env][name]
    write_file(data)


def _guard_valid_env_deletion(name: str):
    if name == "default":
        raise EnvironmentProtectedError(name)


def set_active(name: str):
    data = read_env_file()
    _guard_valid_env_name(data, name)
    data["active"] = name
    write_file(data)


def _guard_valid_env_name(env: Any, name: str):
    envs = env.get("environments", {})
    if name not in envs:
        raise UnknownEnvironmentError(name)


def create_new_env(name: str, template: str):
    data = read_env_file()
    _guard_env_unique(data, name)
    new_env = {}
    if template:
        _guard_valid_env_name(data, template)
        new_env = data["environments"][template]

    data["active"] = name
    data.setdefault("environments", {})
    data["environments"][name] = new_env
    write_file(data)


def _guard_env_unique(env: Any, name: str):
    envs = env.get("environments", {})
    if name in envs:
        raise EnvironmentAlreadyExistsError(name)


def delete_env(name: str):
    _guard_valid_env_deletion(name)
    data = read_env_file()
    data["environments"].pop(name, None)
    if data["active"] == name:
        data["active"] = "default"
    write_file(data)
