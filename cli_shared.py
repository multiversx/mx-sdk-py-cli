import argparse
from argparse import FileType

import sys
from erdpy import config, utils
from typing import Any, Text


def wider_help_formatter(prog: Text):
    return argparse.HelpFormatter(prog, max_help_position=50, width=120)


def add_group_subparser(subparsers: Any, group: str, description: str) -> Any:
    parser = subparsers.add_parser(
        group,
        usage=f"erdpy {group} COMMAND [-h] ...",
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser._positionals.title = "COMMANDS"
    parser._optionals.title = "OPTIONS"

    return parser


def build_group_epilog(subparsers: Any) -> str:
    epilog = """
----------------
COMMANDS summary
----------------
"""
    for choice, sub in subparsers.choices.items():
        epilog += (f"{choice.ljust(30)} {sub.description}\n")

    return epilog


def add_command_subparser(subparsers: Any, group: str, command: str, description: str):
    return subparsers.add_parser(
        command,
        usage=f"erdpy {group} {command} [-h] ...",
        description=description,
        formatter_class=wider_help_formatter
    )


def add_tx_args(sub: Any, with_nonce: bool = True, with_receiver: bool = True, with_data: bool = True):
    if with_nonce:
        sub.add_argument("--nonce", type=int, required=not("--recall-nonce" in sys.argv), help="# the nonce for the transaction")
        sub.add_argument("--recall-nonce", action="store_true", default=False, help="⭮ whether to recall the nonce when creating the transaction (default: %(default)s)")

    if with_receiver:
        sub.add_argument("--receiver", required=True, help="🖄 the address of the receiver")

    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE, help="⛽ the gas price (default: %(default)d)")
    sub.add_argument("--gas-limit", required=True, help="⛽ the gas limit")
    sub.add_argument("--value", default="0", help="the value to transfer (default: %(default)s)")

    if with_data:
        sub.add_argument("--data", default="", help="the payload, or 'memo' of the transaction (default: %(default)s)")

    sub.add_argument("--chain", default=config.get_chain_id(), help="the chain identifier (default: %(default)s)")
    sub.add_argument("--version", type=int, default=config.get_tx_version(), help="the transaction version (default: %(default)s)")


def add_wallet_args(sub: Any):
    sub.add_argument("--pem", required=not (utils.is_arg_present("--keyfile", sys.argv)), help="🔑 the PEM file, if keyfile not provided")
    sub.add_argument("--keyfile", required=not (utils.is_arg_present("--pem", sys.argv)), help="🔑 a JSON keyfile, if PEM not provided")
    sub.add_argument("--passfile", required=not (utils.is_arg_present("--pem", sys.argv)), help="🔑 a file containing keyfile's password, if keyfile provided")


def add_proxy_arg(sub: Any):
    sub.add_argument("--proxy", default=config.get_proxy(), help="🖧 the URL of the proxy (default: %(default)s)")


def add_outfile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument("--outfile", type=FileType("w"), default=sys.stdout, help=f"where to save the output {what} (default: stdout)")


def add_infile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument("--infile", type=FileType("r"), default=None, help=f"input file {what}")
