import logging
from pathlib import Path
from typing import Any, List

from multiversx_sdk import ProxyNetworkProvider

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.config import get_config_for_network_providers
from multiversx_sdk_cli.cosign_transaction import cosign_transaction
from multiversx_sdk_cli.errors import IncorrectWalletError, NoWalletProvided
from multiversx_sdk_cli.transactions import (
    do_prepare_transaction,
    load_transaction_from_file,
)

logger = logging.getLogger("cli.transactions")


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "tx", "Create and broadcast Transactions")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(
        subparsers,
        "tx",
        "new",
        f"Create a new transaction.{CLIOutputBuilder.describe()}",
    )
    _add_common_arguments(args, sub)
    cli_shared.add_token_transfers_args(sub)
    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.add_argument(
        "--wait-result",
        action="store_true",
        default=False,
        help="signal to wait for the transaction result - only valid if --send is set",
    )
    sub.add_argument(
        "--timeout",
        default=100,
        help="max num of seconds to wait for result" " - only valid if --wait-result is set",
    )
    sub.set_defaults(func=create_transaction)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "tx",
        "send",
        f"Send a previously saved transaction.{CLIOutputBuilder.describe()}",
    )
    cli_shared.add_infile_arg(sub, what="a previously saved transaction")
    cli_shared.add_outfile_arg(sub, what="the hash")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=send_transaction)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "tx",
        "get",
        f"Get a transaction.{CLIOutputBuilder.describe(with_emitted=False, with_transaction_on_network=True)}",
    )
    sub.add_argument("--hash", required=True, help="the hash")
    sub.add_argument("--sender", required=False, help="the sender address")
    sub.add_argument(
        "--with-results",
        action="store_true",
        help="will also return the results of transaction",
    )
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_omit_fields_arg(sub)
    sub.set_defaults(func=get_transaction)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "tx",
        "sign",
        f"Sign a previously saved transaction.{CLIOutputBuilder.describe()}",
    )
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_infile_arg(sub, what="a previously saved transaction")
    cli_shared.add_outfile_arg(sub, what="the signed transaction")
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)
    sub.set_defaults(func=sign_transaction)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "tx",
        "relay",
        f"Relay a previously saved transaction.{CLIOutputBuilder.describe()}",
    )
    cli_shared.add_relayed_v3_wallet_args(args, sub)
    cli_shared.add_infile_arg(sub, what="a previously saved transaction")
    cli_shared.add_outfile_arg(sub, what="the relayer signed transaction")
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=relay_transaction)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_common_arguments(args: List[str], sub: Any):
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub)
    sub.add_argument("--data-file", type=str, default=None, help="a file containing transaction data")


def create_transaction(args: Any):
    args = utils.as_object(args)

    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    if args.data_file:
        args.data = Path(args.data_file).read_text()

    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def send_transaction(args: Any):
    args = utils.as_object(args)

    tx = load_transaction_from_file(args.infile)
    output = CLIOutputBuilder()

    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)

    try:
        tx_hash = proxy.send_transaction(tx)
        output.set_emitted_transaction_hash(tx_hash.hex())
    finally:
        output = output.set_emitted_transaction(tx).build()
        utils.dump_out_json(output, outfile=args.outfile)


def get_transaction(args: Any):
    args = utils.as_object(args)
    omit_fields = cli_shared.parse_omit_fields_arg(args)

    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)

    transaction = proxy.get_transaction(args.hash)
    output = CLIOutputBuilder().set_transaction_on_network(transaction, omit_fields).build()
    utils.dump_out_json(output)


def sign_transaction(args: Any):
    args = utils.as_object(args)

    cli_shared.check_guardian_args(args)
    cli_shared.check_broadcast_args(args)

    tx = load_transaction_from_file(args.infile)
    if args.guardian:
        cli_shared.check_options_for_guarded_tx(tx.options)

    account = cli_shared.prepare_account(args)
    tx.signature = account.sign_transaction(tx)

    try:
        guardian_account = cli_shared.prepare_guardian_account(args)
    except NoWalletProvided:
        guardian_account = None

    if guardian_account:
        tx.guardian_signature = guardian_account.sign_transaction(tx)
    elif args.guardian:
        tx = cosign_transaction(tx, args.guardian_service_url, args.guardian_2fa_code)

    cli_shared.send_or_simulate(tx, args)


def relay_transaction(args: Any):
    args = utils.as_object(args)

    if not _is_relayer_wallet_provided(args):
        raise NoWalletProvided()

    cli_shared.check_broadcast_args(args)

    tx = load_transaction_from_file(args.infile)
    relayer = cli_shared.prepare_relayer_account(args)

    if tx.relayer != relayer.address:
        raise IncorrectWalletError("Relayer wallet does not match the relayer's address set in the transaction.")

    tx.relayer_signature = relayer.sign_transaction(tx)

    cli_shared.send_or_simulate(tx, args)


def _is_relayer_wallet_provided(args: Any):
    return any([args.relayer_pem, args.relayer_keyfile, args.relayer_ledger])
