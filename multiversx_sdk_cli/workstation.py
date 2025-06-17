import sys
from pathlib import Path

from multiversx_sdk_cli import utils
from multiversx_sdk_cli.constants import SDK_PATH


def get_tools_folder() -> Path:
    folder = SDK_PATH
    utils.ensure_folder(folder)
    return folder


def is_linux():
    return get_platform() == "linux"


def is_windows():
    return get_platform() == "windows"


def is_osx():
    return get_platform() == "osx"


def get_platform():
    platforms = {
        "linux": "linux",
        "linux1": "linux",
        "linux2": "linux",
        "darwin": "osx",
        "win32": "windows",
        "cygwin": "windows",
        "msys": "windows",
    }

    platform = platforms.get(sys.platform)
    if platform is None:
        raise Exception(f"Unknown platform: {sys.platform}")

    return platform
