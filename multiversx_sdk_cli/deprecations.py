from pathlib import Path
from typing import Any

from multiversx_sdk_cli import ux


def relay_cli_argument_is_deprecated():
    ux.show_deprecation_warning("""The CLI argument '--relay' is deprecated and will be removed in the next major version.
Watch https://github.com/multiversx/mx-sdk-py-core for updates on crafting relayed transactions.""")


def cli_argument_added_in_mxpy_json_is_deprecated(value: Any, name: str, config_file: Path):
    if value:
        ux.show_deprecation_warning(f"You've previously configured a value for '{name}' in the configuration file {config_file}. This is now deprecated. Please use explicit command-line arguments, instead.")


def cli_subcommand_arguments_in_mxpy_json_is_deprecated(config_file: Path):
    ux.show_deprecation_warning(f"""It seems that you've previously set CLI arguments in the configuration file {config_file}. 
This is no longer recommended. Please see https://docs.multiversx.com/sdk-and-tools/sdk-py/mxpy-cli.""")
