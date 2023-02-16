import importlib.metadata
import logging
from pathlib import Path

import toml


def get_version() -> str:
    try:
        # Works for local development
        return _get_version_from_pyproject()
    except Exception as error:
        try:
            # Works for the installed package
            return _get_version_from_metadata()
        except Exception as error:
            logging.exception(f"Failed to get version: {error}")
            return "unknown"


def _get_version_from_pyproject() -> str:
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    version: str = toml.load(pyproject_path)["project"]["version"]
    return version


def _get_version_from_metadata() -> str:
    return importlib.metadata.version("multiversx_sdk_cli")
