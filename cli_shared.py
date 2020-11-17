import argparse
import ast
import sys
from argparse import FileType
from typing import Any, List, Text

from erdpy import config, errors, scope, utils
from erdpy.accounts import Account
from erdpy.proxy.core import ElrondProxy


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
        epilog += f"{choice.ljust(30)} {sub.description}\n"

    return epilog


def add_command_subparser(subparsers: Any, group: str, command: str, description: str):
    return subparsers.add_parser(
        command,
        usage=f"erdpy {group} {command} [-h] ...",
        description=description,
        formatter_class=wider_help_formatter
    )


def add_tx_args(sub: Any, with_nonce: bool = True, with_receiver: bool = True, with_data: bool = True, with_estimate_gas: bool = False):
    if with_nonce:
        sub.add_argument("--nonce", type=int, required=not("--recall-nonce" in sys.argv), help="# the nonce for the transaction")
        sub.add_argument("--recall-nonce", action="store_true", default=False, help="⭮ whether to recall the nonce when creating the transaction (default: %(default)s)")

    if with_receiver:
        sub.add_argument("--receiver", required=True, help="🖄 the address of the receiver")

    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE, help="⛽ the gas price (default: %(default)d)")
    sub.add_argument("--gas-limit", required=not("--estimate-gas" in sys.argv), help="⛽ the gas limit")
    if with_estimate_gas:
        sub.add_argument("--estimate-gas", action="store_true", default=False, help="⛽ whether to estimate the gas limit (default: %(default)d)")

    sub.add_argument("--value", default="0", help="the value to transfer (default: %(default)s)")

    if with_data:
        sub.add_argument("--data", default="", help="the payload, or 'memo' of the transaction (default: %(default)s)")

    sub.add_argument("--chain", default=scope.get_chain_id(), help="the chain identifier (default: %(default)s)")
    sub.add_argument("--version", type=int, default=scope.get_tx_version(), help="the transaction version (default: %(default)s)")


def add_wallet_args(sub: Any):
    sub.add_argument("--pem", required=not (utils.is_arg_present("--keyfile", sys.argv)), help="🔑 the PEM file, if keyfile not provided")
    sub.add_argument("--pem-index", default=0, help="🔑 the index in the PEM file (default: %(default)s)")
    sub.add_argument("--keyfile", required=not (utils.is_arg_present("--pem", sys.argv)), help="🔑 a JSON keyfile, if PEM not provided")
    sub.add_argument("--passfile", required=not (utils.is_arg_present("--pem", sys.argv)), help="🔑 a file containing keyfile's password, if keyfile provided")


def add_proxy_arg(sub: Any):
    sub.add_argument("--proxy", default=scope.get_proxy(), help="🖧 the URL of the proxy (default: %(default)s)")


def add_outfile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument("--outfile", type=FileType("w"), default=sys.stdout, help=f"where to save the output {what} (default: stdout)")


def add_infile_arg(sub: Any, what: str = ""):
    what = f"({what})" if what else ""
    sub.add_argument("--infile", type=FileType("r"), required=True, help=f"input file {what}")


def add_omit_fields_arg(sub: Any):
    sub.add_argument("--omit-fields", default="[]", type=str, required=False, help="omit fields in the output payload (default: %(default)s)")


def parse_omit_fields_arg(args: Any) -> List[str]:
    literal = args.omit_fields
    parsed = ast.literal_eval(literal)
    return parsed


def prepare_nonce_in_args(args: Any):
    if args.recall_nonce:
        if args.pem:
            account = Account(pem_file=args.pem, pem_index=args.pem_index)
        elif args.keyfile and args.passfile:
            account = Account(key_file=args.keyfile, pass_file=args.passfile)
        else:
            raise errors.NoWalletProvided()

        account.sync_nonce(ElrondProxy(args.proxy))
        args.nonce = account.nonce


def add_broadcast_args(sub: Any, simulate=True, relay=False):
    sub.add_argument("--send", action="store_true", default=False, help="✓ whether to broadcast the transaction (default: %(default)s)")

    if simulate:
        sub.add_argument("--simulate", action="store_true", default=False, help="whether to simulate the transaction (default: %(default)s)")
    if relay:
        sub.add_argument("--relay", action="store_true", default=False, help="whether to relay the transaction (default: %(default)s)")


def check_broadcast_args(args: Any):
    if hasattr(args, "relay") and args.relay and args.send:
        raise errors.BadUsage("Cannot directly send a relayed transaction. Use 'erdpy tx new --relay' first, then 'erdpy tx send --data-file'")
    if args.send and args.simulate:
        raise errors.BadUsage("Cannot both 'simulate' and 'send' a transaction")
