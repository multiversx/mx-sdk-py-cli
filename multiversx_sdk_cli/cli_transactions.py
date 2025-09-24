import logging
from pathlib import Path
from typing import Any

from multiversx_sdk import (
    Address,
    ProxyNetworkProvider,
    TransactionComputer,
    TransfersController,
)

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.args_validation import (
    ensure_relayer_wallet_args_are_provided,
    validate_broadcast_args,
    validate_chain_id_args,
    validate_nonce_args,
    validate_proxy_argument,
    validate_receiver_args,
)
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.config import get_config_for_network_providers
from multiversx_sdk_cli.errors import BadUsage, IncorrectWalletError, NoWalletProvided
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.signing_wrapper import SigningWrapper
from multiversx_sdk_cli.transactions import load_transaction_from_file

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

    if args.data_file:
        args.data = Path(args.data_file).read_text()

    transfers = getattr(args, "token_transfers", None)

    if transfers and args.data:
        raise BadUsage("You cannot provide both data and token transfers")

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    native_amount = int(args.value)
    receiver = Address.new_from_bech32(args.receiver)
    transfers = cli_shared.prepare_token_transfers(transfers) if transfers else None

    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TransfersController(chain_id=chain_id, gas_limit_estimator=gas_estimator)

    if not transfers:
        tx = controller.create_transaction_for_native_token_transfer(
            sender=sender,
            nonce=sender.nonce,
            receiver=receiver,
            native_transfer_amount=native_amount,
            data=args.data.encode() if args.data else None,
            guardian=guardian_and_relayer_data.guardian_address,
            relayer=guardian_and_relayer_data.relayer_address,
            gas_limit=args.gas_limit,
            gas_price=args.gas_price,
        )
    else:
        tx = controller.create_transaction_for_transfer(
            sender=sender,
            nonce=sender.nonce,
            receiver=receiver,
            native_transfer_amount=native_amount,
            token_transfers=transfers,
            guardian=guardian_and_relayer_data.guardian_address,
            relayer=guardian_and_relayer_data.relayer_address,
            gas_limit=args.gas_limit,
            gas_price=args.gas_price,
        )

    cli_shared.alter_transaction_and_sign_again_if_needed(
        args=args,
        tx=tx,
        sender=sender,
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
            raise BadUsage("Guardian wallet provided but the transaction has incorrect options")

    guardian_and_relayer = GuardianRelayerData(
        guardian=guardian,
        guardian_address=tx.guardian,
        relayer=relayer,
        relayer_address=tx.relayer,
        guardian_service_url=args.guardian_service_url,
        guardian_2fa_code=args.guardian_2fa_code,
    )

    signer = SigningWrapper()
    signer.sign_transaction(
        transaction=tx,
        sender=sender,
        guardian_and_relayer=guardian_and_relayer,
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
