import logging
from pathlib import Path

import toml


def get_version():
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        version = toml.load(pyproject_path)["project"]["version"]
    except Exception as error:
        logging.exception(f"Failed to get version: {error}")
        version = "unknown"
    return version
