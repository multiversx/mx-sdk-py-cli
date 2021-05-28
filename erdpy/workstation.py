import sys
from pathlib import Path

from erdpy import config, utils


def get_tools_folder():
    folder = Path.home() / config.ROOT_FOLDER_NAME
    utils.ensure_folder(folder)
    return folder


def get_platform():
    platforms = {
        "linux": "linux",
        "linux1": "linux",
        "linux2": "linux",
        "darwin": "osx",
        "win32": "windows",
        "cygwin": "windows",
        "msys": "windows"
    }

    platform = platforms.get(sys.platform)
    if platform is None:
        raise Exception(f"Unknown platform: {sys.platform}")

    return platform
