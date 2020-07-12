from erdpy import cli_shared
import os
import sys
from argparse import FileType
from typing import Any

from erdpy import config, facade, transactions
from erdpy.utils import is_arg_present


def setup_parser(subparsers: Any) -> Any:
    # # DEPRECATED
    # sub = subparsers.add_parser("tx-prepare")
    # _add_common_arguments(sub)
    # sub.add_argument("--tag", default="untitled")
    # sub.add_argument("workspace", nargs='?', default=os.getcwd())
    # sub.set_defaults(func=tx_prepare)

    # # DEPRECATED
    # sub = subparsers.add_parser("tx-send")
    # sub.add_argument("tx")
    # sub.add_argument("--proxy", required=True)
    # sub.set_defaults(func=tx_send)

    # # DEPRECATED
    # sub = subparsers.add_parser("tx-prepare-and-send")
    # _add_common_arguments(sub)
    # sub.add_argument("--proxy", required=True)
    # sub.set_defaults(func=tx_prepare_and_send)

    # NEW API
    parser = cli_shared.add_group_subparser(subparsers, "tx", "Create and broadcast Transactions")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "tx", "new", "Create a new transaction")
    _add_common_arguments(sub)
    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    sub.add_argument("--send", action="store_true", default=False, help="✓ whether to broadcast (send) the transaction (default: %(default)s)")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=create_transaction)

    sub = cli_shared.add_command_subparser(subparsers, "tx", "send", "Send a previously saved transaction")
    cli_shared.add_infile_arg(sub, what="a previously saved transaction")
    cli_shared.add_outfile_arg(sub, what="the hash")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=send_transaction)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_common_arguments(sub: Any):
    cli_shared.add_wallet_args(sub)
    cli_shared.add_tx_args(sub)
    sub.add_argument("--data-file", type=FileType("r"), default=None, help="a file containing transaction data")


def tx_prepare(args: Any):
    transactions.prepare(args)


def tx_send(args: Any):
    facade.send_prepared_transaction(args)


def tx_prepare_and_send(args: Any):
    facade.prepare_and_send_transaction(args)


def create_transaction(args: Any):
    facade.create_transaction(args)


def send_transaction(args: Any):
    facade.send_transaction(args)
