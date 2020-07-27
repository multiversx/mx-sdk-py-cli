from erdpy import cli_shared
from argparse import FileType
from typing import Any

from erdpy import facade


def setup_parser(subparsers: Any) -> Any:
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

    sub = cli_shared.add_command_subparser(subparsers, "tx", "get", "Get a transaction")
    sub.add_argument("--hash", required=True, help="the hash")
    sub.add_argument("--sender", required=False, help="the sender address")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_transaction)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_common_arguments(sub: Any):
    cli_shared.add_wallet_args(sub)
    cli_shared.add_tx_args(sub)
    sub.add_argument("--data-file", type=FileType("r"), default=None, help="a file containing transaction data")


def create_transaction(args: Any):
    facade.create_transaction(args)


def send_transaction(args: Any):
    facade.send_transaction(args)


def get_transaction(args: Any):
    facade.get_transaction(args)

