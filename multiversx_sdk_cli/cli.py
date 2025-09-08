# PYTHON_ARGCOMPLETE_OK
import argparse
import logging
import sys
from argparse import ArgumentParser
from typing import Any

import argcomplete
from multiversx_sdk import LibraryConfig
from rich.logging import RichHandler

import multiversx_sdk_cli.cli_config
import multiversx_sdk_cli.cli_config_env
import multiversx_sdk_cli.cli_config_wallet
import multiversx_sdk_cli.cli_contracts
import multiversx_sdk_cli.cli_data
import multiversx_sdk_cli.cli_delegation
import multiversx_sdk_cli.cli_deps
import multiversx_sdk_cli.cli_dns
import multiversx_sdk_cli.cli_faucet
import multiversx_sdk_cli.cli_get
import multiversx_sdk_cli.cli_governance
import multiversx_sdk_cli.cli_ledger
import multiversx_sdk_cli.cli_localnet
import multiversx_sdk_cli.cli_multisig
import multiversx_sdk_cli.cli_token
import multiversx_sdk_cli.cli_transactions
import multiversx_sdk_cli.cli_validator_wallet
import multiversx_sdk_cli.cli_validators
import multiversx_sdk_cli.cli_wallet
import multiversx_sdk_cli.version
from multiversx_sdk_cli import config, errors, utils, ux
from multiversx_sdk_cli.cli_shared import set_proxy_from_config_if_not_provided
from multiversx_sdk_cli.config_env import get_address_hrp
from multiversx_sdk_cli.constants import LOG_LEVELS, SDK_PATH

logger = logging.getLogger("cli")


def main(cli_args: list[str] = sys.argv[1:]):
    try:
        _do_main(cli_args)
    except errors.KnownError as err:
        logger.critical(err.get_pretty())
        ux.show_critical_error(err.get_pretty())
        return 1
    except KeyboardInterrupt:
        print("process killed by user.")
        return 1
    return 0


def _do_main(cli_args: list[str]):
    utils.ensure_folder(SDK_PATH)
    parser = setup_parser(cli_args)
    argcomplete.autocomplete(parser)

    _handle_global_arguments(cli_args)
    args = parser.parse_args(cli_args)

    if args.verbose:
        logging.basicConfig(
            level="DEBUG",
            force=True,
            format="%(name)s: %(message)s",
            handlers=[RichHandler(show_time=False, rich_tracebacks=True)],
        )
    else:
        level: str = args.log_level
        logging.basicConfig(
            level=level.upper(),
            format="%(name)s: %(message)s",
            handlers=[RichHandler(show_time=False, rich_tracebacks=True)],
        )

    verify_deprecated_entries_in_config_file()
    default_hrp = get_address_hrp()
    LibraryConfig.default_address_hrp = default_hrp

    if not hasattr(args, "func"):
        parser.print_help()
    else:
        set_proxy_from_config_if_not_provided(args)
        args.func(args)


def setup_parser(args: list[str]):
    parser = ArgumentParser(
        prog="mxpy",
        usage="mxpy [-h] [-v] [--verbose] COMMAND-GROUP [-h] COMMAND ...",
        description="""
-----------
DESCRIPTION
-----------
mxpy is part of the multiversx-sdk and consists of Command Line Tools and Python SDK
for interacting with the Blockchain (in general) and with Smart Contracts (in particular).

mxpy targets a broad audience of users and developers.

See:
 - https://docs.multiversx.com/sdk-and-tools/sdk-py
 - https://docs.multiversx.com/sdk-and-tools/sdk-py/mxpy-cli
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser._positionals.title = "COMMAND GROUPS"
    parser._optionals.title = "TOP-LEVEL OPTIONS"
    version = multiversx_sdk_cli.version.get_version()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"MultiversX Python CLI (mxpy) {version}",
    )
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument(
        "--log-level",
        type=str,
        default=config.get_log_level_from_config(),
        choices=LOG_LEVELS,
        help="default: %(default)s",
    )

    subparsers = parser.add_subparsers()
    commands: list[Any] = []

    commands.append(multiversx_sdk_cli.cli_config_wallet.setup_parser(subparsers))
    commands.append(multiversx_sdk_cli.cli_contracts.setup_parser(args, subparsers))
    commands.append(multiversx_sdk_cli.cli_transactions.setup_parser(args, subparsers))
    commands.append(multiversx_sdk_cli.cli_validators.setup_parser(args, subparsers))
    commands.append(multiversx_sdk_cli.cli_ledger.setup_parser(subparsers))
    commands.append(multiversx_sdk_cli.cli_wallet.setup_parser(args, subparsers))
    commands.append(multiversx_sdk_cli.cli_validator_wallet.setup_parser(args, subparsers))
    commands.append(multiversx_sdk_cli.cli_deps.setup_parser(subparsers))
    commands.append(multiversx_sdk_cli.cli_config.setup_parser(subparsers))
    commands.append(multiversx_sdk_cli.cli_localnet.setup_parser(args, subparsers))
    commands.append(multiversx_sdk_cli.cli_data.setup_parser(subparsers))
    commands.append(multiversx_sdk_cli.cli_delegation.setup_parser(args, subparsers))
    commands.append(multiversx_sdk_cli.cli_dns.setup_parser(args, subparsers))
    commands.append(multiversx_sdk_cli.cli_faucet.setup_parser(args, subparsers))
    commands.append(multiversx_sdk_cli.cli_multisig.setup_parser(args, subparsers))
    commands.append(multiversx_sdk_cli.cli_governance.setup_parser(args, subparsers))
    commands.append(multiversx_sdk_cli.cli_config_env.setup_parser(subparsers))
    commands.append(multiversx_sdk_cli.cli_get.setup_parser(subparsers))
    commands.append(multiversx_sdk_cli.cli_token.setup_parser(args, subparsers))

    parser.epilog = """
----------------------
COMMAND GROUPS summary
----------------------
"""
    for choice, sub in subparsers.choices.items():
        parser.epilog += f"{choice.ljust(30)} {sub.description}\n"

    return parser


def verify_deprecated_entries_in_config_file():
    deprecated_keys = config.get_deprecated_entries_in_config_file()
    if len(deprecated_keys) == 0:
        return

    config_path = config.resolve_config_path()
    message = f"The following config entries are deprecated. Please access `{str(config_path)}` and remove them. \n"
    for entry in deprecated_keys:
        message += f"-> {entry} \n"

    ux.show_warning(message.rstrip("\n"))


def _handle_global_arguments(args: list[str]):
    """
    Handle global arguments like --verbose and --log-level.
    """
    log_level_arg = "--log-level"
    if log_level_arg in args:
        index = args.index(log_level_arg)
        if index + 1 >= len(args):
            raise ValueError(f"Argument {log_level_arg} must be followed by a log level value.")

        log_arg = args.pop(index)
        log_value = args.pop(index)
        args.insert(0, log_value)
        args.insert(0, log_arg)

    if "--verbose" in args:
        args.remove("--verbose")
        args.insert(0, "--verbose")


if __name__ == "__main__":
    ret = main(sys.argv[1:])
    sys.exit(ret)
