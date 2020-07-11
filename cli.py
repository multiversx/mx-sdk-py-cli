import logging
import sys
import argparse
from argparse import ArgumentParser
from typing import Any, List

from erdpy import (cli_accounts, cli_blockatlas, cli_config, cli_contracts,
                   cli_cost, cli_deps, cli_dispatcher, cli_network,
                   cli_transactions, cli_validators, cli_wallet, errors)
from erdpy._version import __version__

logger = logging.getLogger("cli")


def main():
    try:
        _do_main()
    except errors.KnownError as err:
        logger.critical(err.get_pretty())
        sys.exit(1)


def _do_main():
    parser = setup_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARN)

    if not hasattr(args, "func"):
        parser.print_help()
    else:
        args.func(args)


def setup_parser():
    parser = ArgumentParser(
        prog="erdpy",
        usage="erdpy [-h] [-v] [--verbose] COMMAND-GROUP [-h] COMMAND options",
        description="""
-----------
DESCRIPTION
-----------
erdpy is part of the elrond-sdk and consists of Command Line Tools and Python SDK
for interacting with the Blockchain (in general) and with Smart Contracts (in particular).

erdpy targets a broad audience of users and developers.
https://docs.elrond.com/tools/erdpy.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser._positionals.title = "COMMAND GROUPS"
    parser._optionals.title = "TOP-LEVEL OPTIONS"

    parser.add_argument("-v", "--version", action="version", version=f"erdpy {__version__}")
    parser.add_argument("--verbose", action="store_true", default=False)

    subparsers = parser.add_subparsers()
    commands: List[Any] = []

    commands.append(cli_contracts.setup_parser(subparsers))
    commands.append(cli_transactions.setup_parser(subparsers))
    commands.append(cli_validators.setup_parser(subparsers))
    commands.append(cli_accounts.setup_parser(subparsers))
    commands.append(cli_wallet.setup_parser(subparsers))
    commands.append(cli_network.setup_parser(subparsers))
    commands.append(cli_cost.setup_parser(subparsers))
    commands.append(cli_dispatcher.setup_parser(subparsers))
    commands.append(cli_blockatlas.setup_parser(subparsers))
    commands.append(cli_deps.setup_parser(subparsers))
    commands.append(cli_config.setup_parser(subparsers))

    parser.epilog = """
----------------------
COMMAND GROUPS summary
----------------------
"""
    for choice, sub in subparsers.choices.items():
        parser.epilog += (f"{choice.ljust(30)} {sub.description}\n")

    return parser


if __name__ == "__main__":
    main()
