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
    cli_shared.add_broadcast_args(sub, relay=True)
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
    sub.add_argument("--with-results", action="store_true", help="will also return the results of transaction")
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_omit_fields_arg(sub)
    sub.set_defaults(func=get_transaction)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_common_arguments(sub: Any):
    cli_shared.add_wallet_args(sub)
    cli_shared.add_tx_args(sub)
    sub.add_argument("--data-file", type=FileType("r"), default=None, help="a file containing transaction data")


def create_transaction(args: Any):
    args = utils.as_object(args)

    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)

    if args.data_file:
        args.data = utils.read_file(args.data_file)

    tx = do_prepare_transaction(args)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(tx.serialize_as_inner())
        return

    try:
        if args.send:
            tx.send(ElrondProxy(args.proxy))
        elif args.simulate:
            response = tx.simulate(ElrondProxy(args.proxy))
            utils.dump_out_json(response)
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
    omit_fields = cli_shared.parse_omit_fields_arg(args)

    proxy = ElrondProxy(args.proxy)

    transaction = proxy.get_transaction(args.hash, args.sender, args.with_results)
    utils.omit_fields(transaction, omit_fields)
    utils.dump_out_json(transaction)
