from argparse import FileType
from typing import Any

from erdpy import cli_shared, utils
from erdpy.proxy.core import ElrondProxy
from erdpy.transactions import Transaction, do_prepare_transaction


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "tx", "Create and broadcast Transactions")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "tx", "new", "Create a new transaction")
    _add_common_arguments(sub)
    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    sub.add_argument("--send", action="store_true", default=False, help="✓ whether to broadcast (send) the transaction (default: %(default)s)")
    sub.add_argument("--relay", action="store_true", default=False, help="whether to relay the transaction (default: %(default)s)")
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
    args = utils.as_object(args)

    cli_shared.prepare_nonce_in_args(args)

    if args.data_file:
        args.data = utils.read_file(args.data_file)

    tx = do_prepare_transaction(args)

    if args.relay:
        args.outfile.write(tx.serialize_as_inner())
        return

    try:
        if args.send:
            tx.send(ElrondProxy(args.proxy))
    finally:
        tx.dump_to(args.outfile)


def send_transaction(args: Any):
    args = utils.as_object(args)

    tx = Transaction.load_from_file(args.infile)

    try:
        tx.send(ElrondProxy(args.proxy))
    finally:
        tx.dump_to(args.outfile)


def get_transaction(args: Any):
    args = utils.as_object(args)

    proxy = ElrondProxy(args.proxy)

    response = proxy.get_transaction(args.hash, args.sender)
    print(response)
