import argparse
import logging
import sys
from argparse import ArgumentParser
from typing import Any, List

import erdpy.cli_accounts
import erdpy.cli_block
import erdpy.cli_config
import erdpy.cli_contracts
import erdpy.cli_data
import erdpy.cli_deps
import erdpy.cli_ledger
import erdpy.cli_network
import erdpy.cli_testnet
import erdpy.cli_transactions
import erdpy.cli_validators
import erdpy.cli_wallet
import erdpy.cli_delegation
import erdpy.cli_dns
from erdpy import config, errors, scope
from erdpy._version import __version__

logger = logging.getLogger("cli")


def main():
    try:
        _do_main()
    except errors.KnownError as err:
        logger.critical(err.get_pretty())
        return 1
    except KeyboardInterrupt:
        print("erdpy process killed by user.")
        return 1
    return 0


def _do_main():
    logging.basicConfig(level=logging.INFO)
    scope.initialize()

    argv_with_config_args = config.add_config_args(sys.argv[1:])
    parser = setup_parser(argv_with_config_args)
    args = parser.parse_args(argv_with_config_args)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARN)

    if not hasattr(args, "func"):
        parser.print_help()
    else:
        args.func(args)


def setup_parser(args: List[str] = sys.argv[1:]):
    parser = ArgumentParser(
        prog="erdpy",
        usage="erdpy [-h] [-v] [--verbose] COMMAND-GROUP [-h] COMMAND ...",
        description="""
-----------
DESCRIPTION
-----------
erdpy is part of the elrond-sdk and consists of Command Line Tools and Python SDK
for interacting with the Blockchain (in general) and with Smart Contracts (in particular).

erdpy targets a broad audience of users and developers.
https://docs.elrond.com/sdk-and-tools/erdpy/erdpy.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser._positionals.title = "COMMAND GROUPS"
    parser._optionals.title = "TOP-LEVEL OPTIONS"

    parser.add_argument("-v", "--version", action="version", version=f"erdpy {__version__}")
    parser.add_argument("--verbose", action="store_true", default=False)

    subparsers = parser.add_subparsers()
    commands: List[Any] = []

    commands.append(erdpy.cli_contracts.setup_parser(args, subparsers))
    commands.append(erdpy.cli_transactions.setup_parser(args, subparsers))
    commands.append(erdpy.cli_validators.setup_parser(args, subparsers))
    commands.append(erdpy.cli_accounts.setup_parser(subparsers))
    commands.append(erdpy.cli_ledger.setup_parser(subparsers))
    commands.append(erdpy.cli_wallet.setup_parser(args, subparsers))
    commands.append(erdpy.cli_network.setup_parser(subparsers))
    commands.append(erdpy.cli_deps.setup_parser(subparsers))
    commands.append(erdpy.cli_config.setup_parser(subparsers))
    commands.append(erdpy.cli_block.setup_parser(subparsers))
    commands.append(erdpy.cli_testnet.setup_parser(args, subparsers))
    commands.append(erdpy.cli_data.setup_parser(subparsers))
    commands.append(erdpy.cli_delegation.setup_parser(args, subparsers))
    commands.append(erdpy.cli_dns.setup_parser(args, subparsers))

    parser.epilog = """
----------------------
COMMAND GROUPS summary
----------------------
"""
    for choice, sub in subparsers.choices.items():
        parser.epilog += (f"{choice.ljust(30)} {sub.description}\n")

    return parser


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
