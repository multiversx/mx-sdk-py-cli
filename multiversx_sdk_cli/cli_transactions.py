from argparse import FileType
from typing import Any, List

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_network_providers.proxy_network_provider import ProxyNetworkProvider
from multiversx_sdk_cli.transactions import Transaction, do_prepare_transaction


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "tx", "Create and broadcast Transactions")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "tx", "new", f"Create a new transaction.{CLIOutputBuilder.describe()}")
    _add_common_arguments(args, sub)
    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=create_transaction)

    sub = cli_shared.add_command_subparser(subparsers, "tx", "send", f"Send a previously saved transaction.{CLIOutputBuilder.describe()}")
    cli_shared.add_infile_arg(sub, what="a previously saved transaction")
    cli_shared.add_outfile_arg(sub, what="the hash")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=send_transaction)

    sub = cli_shared.add_command_subparser(subparsers, "tx", "get", f"Get a transaction.{CLIOutputBuilder.describe(with_emitted=False, with_transaction_on_network=True)}")
    sub.add_argument("--hash", required=True, help="the hash")
    sub.add_argument("--sender", required=False, help="the sender address")
    sub.add_argument("--with-results", action="store_true", help="will also return the results of transaction")
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_omit_fields_arg(sub)
    sub.set_defaults(func=get_transaction)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_common_arguments(args: List[str], sub: Any):
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub)
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

    cli_shared.send_or_simulate(tx, args)


def send_transaction(args: Any):
    args = utils.as_object(args)

    tx = Transaction.load_from_file(args.infile)

    try:
        tx.send(ProxyNetworkProvider(args.proxy))
    finally:
        output = CLIOutputBuilder().set_emitted_transaction(tx).build()
        utils.dump_out_json(output, outfile=args.outfile)


def get_transaction(args: Any):
    args = utils.as_object(args)
    omit_fields = cli_shared.parse_omit_fields_arg(args)
    proxy = ProxyNetworkProvider(args.proxy)

    transaction = proxy.get_transaction(args.hash)
    output = CLIOutputBuilder().set_transaction_on_network(transaction, omit_fields).build()
    utils.dump_out_json(output)
