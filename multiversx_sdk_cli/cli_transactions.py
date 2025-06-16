import logging
from pathlib import Path
from typing import Any

from multiversx_sdk import Address, ProxyNetworkProvider, TransactionComputer

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.args_validation import (
    ensure_relayer_wallet_args_are_provided,
    validate_broadcast_args,
    validate_chain_id_args,
    validate_nonce_args,
    validate_proxy_argument,
    validate_receiver_args,
)
from multiversx_sdk_cli.base_transactions_controller import BaseTransactionsController
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.config import get_config_for_network_providers
from multiversx_sdk_cli.errors import BadUsage, IncorrectWalletError, NoWalletProvided
from multiversx_sdk_cli.transactions import (
    TransactionsController,
    load_transaction_from_file,
)

logger = logging.getLogger("cli.transactions")


def setup_parser(args: list[str], subparsers: Any) -> Any:
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

    cli_shared.add_wait_result_and_timeout_args(sub)
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
        "sign",
        f"Sign a previously saved transaction.{CLIOutputBuilder.describe()}",
    )
    cli_shared.add_wallet_args(args=args, sub=sub)
    cli_shared.add_infile_arg(sub, what="a previously saved transaction")
    cli_shared.add_outfile_arg(sub, what="the signed transaction")
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_proxy_arg(sub)
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


def _add_common_arguments(args: list[str], sub: Any):
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub)
    sub.add_argument("--data-file", type=str, default=None, help="a file containing transaction data")


def create_transaction(args: Any):
    validate_nonce_args(args)
    validate_receiver_args(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    if args.data_file:
        args.data = Path(args.data_file).read_text()

    native_amount = int(args.value)
    gas_limit = int(args.gas_limit) if args.gas_limit else 0

    transfers = getattr(args, "token_transfers", None)
    transfers = cli_shared.prepare_token_transfers(transfers) if transfers else None

    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    tx_controller = TransactionsController(chain_id)

    tx = tx_controller.create_transaction(
        sender=sender,
        receiver=Address.new_from_bech32(args.receiver),
        native_amount=native_amount,
        gas_limit=gas_limit,
        gas_price=args.gas_price,
        nonce=sender.nonce,
        version=args.version,
        options=args.options,
        token_transfers=transfers,
        data=args.data,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def send_transaction(args: Any):
    validate_proxy_argument(args)

    tx = load_transaction_from_file(args.infile)
    output = CLIOutputBuilder()

    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)

    try:
        cli_shared._confirm_continuation_if_required(tx)

        tx_hash = proxy.send_transaction(tx)
        output.set_emitted_transaction_hash(tx_hash.hex())
    finally:
        output = output.set_emitted_transaction(tx).build()
        utils.dump_out_json(output, outfile=args.outfile)


def sign_transaction(args: Any):
    validate_broadcast_args(args)

    tx = load_transaction_from_file(args.infile)

    try:
        sender = cli_shared.prepare_account(args)
    except:
        logger.info("No sender wallet provided. Will not sign for the sender.")
        sender = None

    if sender and sender.address != tx.sender:
        raise IncorrectWalletError("Sender's wallet does not match transaction's sender.")

    relayer = cli_shared.load_relayer_account(args)
    if relayer and relayer.address != tx.relayer:
        raise IncorrectWalletError("Relayer's wallet does not match transaction's relayer.")

    guardian = cli_shared.load_guardian_account(args)
    if guardian:
        if guardian.address != tx.guardian:
            raise IncorrectWalletError("Guardian's wallet does not match transaction's guardian.")

        tx_computer = TransactionComputer()
        if tx.guardian and not tx_computer.has_options_set_for_guarded_transaction(tx):
            raise BadUsage("Guardian wallet provided but the transaction has incorrect options.")

    tx_controller = BaseTransactionsController()
    tx_controller.sign_transaction(
        transaction=tx,
        sender=sender,
        guardian=guardian,
        relayer=relayer,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    cli_shared.send_or_simulate(tx, args)


def relay_transaction(args: Any):
    ensure_relayer_wallet_args_are_provided(args)
    validate_broadcast_args(args)

    tx = load_transaction_from_file(args.infile)

    relayer = cli_shared.load_relayer_account(args)
    if relayer is None:
        raise NoWalletProvided()

    if tx.relayer != relayer.address:
        raise IncorrectWalletError("Relayer wallet does not match the relayer's address set in the transaction.")

    tx.relayer_signature = relayer.sign_transaction(tx)

    cli_shared.send_or_simulate(tx, args)
