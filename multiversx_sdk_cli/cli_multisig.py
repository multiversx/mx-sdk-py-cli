import json
import logging
from pathlib import Path
from typing import Any

from multiversx_sdk import (
    Address,
    AddressComputer,
    Token,
    TokenComputer,
    TokenTransfer,
    Transaction,
    TransactionsFactoryConfig,
)
from multiversx_sdk.abi import Abi

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.args_validation import (
    ensure_wallet_args_are_provided,
    validate_broadcast_args,
    validate_chain_id_args,
    validate_transaction_args,
)
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.constants import NUMBER_OF_SHARDS
from multiversx_sdk_cli.multisig import MultisigWrapper

logger = logging.getLogger("cli.multisig")


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers,
        "multisig",
        "Deploy and interact with the Multisig Smart Contract",
    )
    subparsers = parser.add_subparsers()

    output_description = CLIOutputBuilder.describe(
        with_contract=True, with_transaction_on_network=True, with_simulation=True
    )

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "deploy",
        f"Deploy a Multisig Smart Contract.{output_description}",
    )
    _add_bytecode_arg(sub)
    _add_abi_arg(sub)
    sub.add_argument(
        "--quorum",
        type=int,
        required=True,
        help="the number of signatures required to approve a proposal",
    )
    sub.add_argument(
        "--board-members",
        required=True,
        nargs="+",
        type=str,
        help="the bech32 addresses of the board members",
    )
    _add_metadata_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=deploy)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "deposit",
        f"Deposit native tokens (EGLD) or ESDT tokens into a Multisig Smart Contract.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    cli_shared.add_token_transfers_args(sub)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=deposit)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "discard-action",
        f"Discard a proposed action. Signatures must be removed first via `unsign`.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    _add_action_id_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=discard_action)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "discard-batch",
        f"Discard all the actions for the specified IDs.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    sub.add_argument(
        "--action-ids",
        required=True,
        nargs="+",
        type=int,
        help="the IDs of the actions to discard",
    )
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=discard_batch)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "add-board-member",
        f"Propose adding a new board member.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    sub.add_argument(
        "--board-member",
        required=True,
        type=str,
        help="the bech32 address of the proposed board member",
    )
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=add_board_member)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "add-proposer",
        f"Propose adding a new proposer.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    sub.add_argument(
        "--proposer",
        required=True,
        type=str,
        help="the bech32 address of the proposed proposer",
    )
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=add_proposer)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "remove-user",
        f"Propose removing a user from the Multisig Smart Contract.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    sub.add_argument(
        "--user",
        required=True,
        type=str,
        help="the bech32 address of the proposed user to be removed",
    )
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=remove_user)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "change-quorum",
        f"Propose changing the quorum of the Multisig Smart Contract.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    sub.add_argument(
        "--quorum",
        required=True,
        type=int,
        help="the size of the new quorum (number of signatures required to approve a proposal)",
    )
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=change_quorum)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "transfer-and-execute",
        f"Propose transferring EGLD and optionally calling a smart contract.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    sub.add_argument(
        "--opt-gas-limit",
        type=int,
        help="the size of the new quorum (number of signatures required to approve a proposal)",
    )
    sub.add_argument("--contract-abi", type=str, help="the ABI file of the contract to call")
    sub.add_argument("--function", type=str, help="the function to call")
    _add_arguments_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=True, with_data=False)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=transfer_and_execute)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "transfer-and-execute-esdt",
        f"Propose transferring ESDTs and optionally calling a smart contract.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_token_transfers_args(sub)
    sub.add_argument(
        "--opt-gas-limit",
        type=int,
        help="the size of the new quorum (number of signatures required to approve a proposal)",
    )
    sub.add_argument("--contract-abi", type=str, help="the ABI file of the contract to call")
    sub.add_argument("--function", type=str, help="the function to call")
    _add_arguments_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=True, with_data=False)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=transfer_and_execute_esdt)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "async-call",
        f"Propose a transaction in which the contract will perform an async call.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_token_transfers_args(sub)
    sub.add_argument(
        "--opt-gas-limit",
        type=int,
        help="the size of the new quorum (number of signatures required to approve a proposal)",
    )
    sub.add_argument("--contract-abi", type=str, help="the ABI file of the contract to call")
    sub.add_argument("--function", type=str, help="the function to call")
    _add_arguments_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=True, with_data=False)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=async_call)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "deploy-from-source",
        f"Propose a smart contract deploy from a previously deployed smart contract.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)

    sub.add_argument("--contract-abi", type=str, help="the ABI file of the contract to call")
    _add_arguments_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)

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
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=deploy_from_source)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_bytecode_arg(sub: Any):
    sub.add_argument(
        "--bytecode",
        type=str,
        required=True,
        help="the file containing the WASM bytecode",
    )


def _add_contract_arg(sub: Any):
    sub.add_argument("--contract", required=True, type=str, help="🖄 the bech32 address of the Multisig Smart Contract")


def _add_abi_arg(sub: Any):
    sub.add_argument("--abi", required=True, type=str, help="the ABI file of the Multisig Smart Contract")


def _add_action_id_arg(sub: Any):
    sub.add_argument("--action", required=True, type=int, help="the id of the action")


def _add_metadata_arg(sub: Any):
    sub.add_argument(
        "--metadata-not-upgradeable",
        dest="metadata_upgradeable",
        action="store_false",
        help="‼ mark the contract as NOT upgradeable (default: upgradeable)",
    )
    sub.add_argument(
        "--metadata-not-readable",
        dest="metadata_readable",
        action="store_false",
        help="‼ mark the contract as NOT readable (default: readable)",
    )
    sub.add_argument(
        "--metadata-payable",
        dest="metadata_payable",
        action="store_true",
        help="‼ mark the contract as payable (default: not payable)",
    )
    sub.add_argument(
        "--metadata-payable-by-sc",
        dest="metadata_payable_by_sc",
        action="store_true",
        help="‼ mark the contract as payable by SC (default: not payable by SC)",
    )
    sub.set_defaults(metadata_upgradeable=True, metadata_payable=False)


def _add_arguments_arg(sub: Any):
    sub.add_argument(
        "--arguments",
        nargs="+",
        help="arguments for the contract transaction, as [number, bech32-address, ascii string, "
        "boolean] or hex-encoded. E.g. --arguments 42 0x64 1000 0xabba str:TOK-a1c2ef true addr:erd1[..]",
    )
    sub.add_argument(
        "--arguments-file",
        type=str,
        help="a json file containing the arguments. ONLY if abi file is provided. "
        "E.g. [{ 'to': 'erd1...', 'amount': 10000000000 }]",
    )


def deploy(args: Any):
    logger.debug("multisig.deploy")

    validate_transaction_args(args)
    ensure_wallet_args_are_provided(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    abi = Abi.load(Path(args.abi))
    quorum = args.quorum
    board_members = [Address.new_from_bech32(addr) for addr in args.board_members]

    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    tx = multisig.prepare_deploy_transaction(
        owner=sender,
        nonce=sender.nonce,
        bytecode=Path(args.bytecode),
        quorum=quorum,
        board_members=board_members,
        upgradeable=args.metadata_upgradeable,
        readable=args.metadata_readable,
        payable=args.metadata_payable,
        payable_by_sc=args.metadata_payable_by_sc,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    address_computer = AddressComputer(NUMBER_OF_SHARDS)
    contract_address = address_computer.compute_contract_address(deployer=sender.address, deployment_nonce=tx.nonce)

    logger.info("Contract address: %s", contract_address.to_bech32())
    utils.log_explorer_contract_address(args.chain, contract_address.to_bech32())

    _send_or_simulate(tx, contract_address, args)


def deposit(args: Any):
    validate_transaction_args(args)
    ensure_wallet_args_are_provided(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    abi = Abi.load(Path(args.abi))
    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    contract = Address.new_from_bech32(args.contract)
    native_amount = int(args.value)
    token_transfers = _prepare_token_transfers(args.token_transfers)

    tx = multisig.prepare_deposit_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        native_amount=native_amount,
        token_transfers=token_transfers,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def discard_action(args: Any):
    validate_transaction_args(args)
    ensure_wallet_args_are_provided(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    abi = Abi.load(Path(args.abi))
    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    contract = Address.new_from_bech32(args.contract)
    action_id = int(args.action)

    tx = multisig.prepare_discard_action_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        action_id=action_id,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def discard_batch(args: Any):
    validate_transaction_args(args)
    ensure_wallet_args_are_provided(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    abi = Abi.load(Path(args.abi))
    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    contract = Address.new_from_bech32(args.contract)
    actions = args.action_ids

    tx = multisig.prepare_discard_batch_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        action_ids=actions,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def add_board_member(args: Any):
    validate_transaction_args(args)
    ensure_wallet_args_are_provided(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    abi = Abi.load(Path(args.abi))
    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    contract = Address.new_from_bech32(args.contract)
    board_member = Address.new_from_bech32(args.board_member)

    tx = multisig.prepare_add_board_member_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        board_member=board_member,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def add_proposer(args: Any):
    validate_transaction_args(args)
    ensure_wallet_args_are_provided(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    abi = Abi.load(Path(args.abi))
    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    contract = Address.new_from_bech32(args.contract)
    proposer = Address.new_from_bech32(args.proposer)

    tx = multisig.prepare_add_proposer_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        proposer=proposer,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def remove_user(args: Any):
    validate_transaction_args(args)
    ensure_wallet_args_are_provided(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    abi = Abi.load(Path(args.abi))
    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    contract = Address.new_from_bech32(args.contract)
    user = Address.new_from_bech32(args.user)

    tx = multisig.prepare_remove_user_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        user=user,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def change_quorum(args: Any):
    validate_transaction_args(args)
    ensure_wallet_args_are_provided(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    abi = Abi.load(Path(args.abi))
    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    contract = Address.new_from_bech32(args.contract)
    quorum = int(args.quorum)

    tx = multisig.prepare_change_quorum_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        quorum=quorum,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def transfer_and_execute(args: Any):
    validate_transaction_args(args)
    ensure_wallet_args_are_provided(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    abi = Abi.load(Path(args.abi))
    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    contract = Address.new_from_bech32(args.contract)

    receiver = Address.new_from_bech32(args.receiver)
    opt_gas_limit = int(args.opt_gas_limit) if args.opt_gas_limit else None
    function = args.function if args.function else None
    contract_abi = Abi.load(Path(args.contract_abi)) if args.contract_abi else None
    arguments, should_prepare_args = _get_contract_arguments(args)

    tx = multisig.prepare_transfer_execute_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        receiver=receiver,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        should_prepare_args=should_prepare_args,
        guardian_and_relayer_data=guardian_and_relayer_data,
        opt_gas_limit=opt_gas_limit,
        function=function,
        abi=contract_abi,
        arguments=arguments,
        native_token_amount=int(args.value),
    )

    _send_or_simulate(tx, contract, args)


def transfer_and_execute_esdt(args: Any):
    validate_transaction_args(args)
    ensure_wallet_args_are_provided(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    if int(args.value) != 0:
        raise Exception("Native token transfer is not allowed for this command.")

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    abi = Abi.load(Path(args.abi))
    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    contract = Address.new_from_bech32(args.contract)

    receiver = Address.new_from_bech32(args.receiver)
    opt_gas_limit = int(args.opt_gas_limit) if args.opt_gas_limit else None
    function = args.function if args.function else None
    contract_abi = Abi.load(Path(args.contract_abi)) if args.contract_abi else None
    arguments, should_prepare_args = _get_contract_arguments(args)
    token_transfers = _prepare_token_transfers(args.token_transfers)

    tx = multisig.prepare_transfer_execute_esdt_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        receiver=receiver,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        should_prepare_args=should_prepare_args,
        guardian_and_relayer_data=guardian_and_relayer_data,
        token_transfers=token_transfers,
        opt_gas_limit=opt_gas_limit,
        function=function,
        abi=contract_abi,
        arguments=arguments,
    )

    _send_or_simulate(tx, contract, args)


def async_call(args: Any):
    validate_transaction_args(args)
    ensure_wallet_args_are_provided(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    abi = Abi.load(Path(args.abi))
    chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    contract = Address.new_from_bech32(args.contract)

    receiver = Address.new_from_bech32(args.receiver)
    opt_gas_limit = int(args.opt_gas_limit) if args.opt_gas_limit else None
    function = args.function if args.function else None
    contract_abi = Abi.load(Path(args.contract_abi)) if args.contract_abi else None
    arguments, should_prepare_args = _get_contract_arguments(args)
    token_transfers = _prepare_token_transfers(args.token_transfers)

    tx = multisig.prepare_async_call_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        receiver=receiver,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        should_prepare_args=should_prepare_args,
        guardian_and_relayer_data=guardian_and_relayer_data,
        native_token_amount=int(args.value),
        token_transfers=token_transfers,
        opt_gas_limit=opt_gas_limit,
        function=function,
        abi=contract_abi,
        arguments=arguments,
    )

    _send_or_simulate(tx, contract, args)


def deploy_from_source(args: Any):
    pass
    # validate_transaction_args(args)
    # ensure_wallet_args_are_provided(args)
    # validate_broadcast_args(args)
    # validate_chain_id_args(args)

    # sender = cli_shared.prepare_sender(args)
    # guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
    #     sender=sender.address.to_bech32(),
    #     args=args,
    # )

    # abi = Abi.load(Path(args.abi))
    # chain_id = cli_shared.get_chain_id(args.chain, args.proxy)
    # multisig = MultisigWrapper(TransactionsFactoryConfig(chain_id), abi)

    # contract = Address.new_from_bech32(args.contract)

    # receiver = Address.new_from_bech32(args.receiver)
    # opt_gas_limit = int(args.opt_gas_limit) if args.opt_gas_limit else None
    # function = args.function if args.function else None
    # contract_abi = Abi.load(Path(args.contract_abi)) if args.contract_abi else None
    # arguments, should_prepare_args = _get_contract_arguments(args)
    # token_transfers = _prepare_token_transfers(args.token_transfers)

    # tx = multisig.prepare_async_call_transaction(
    #     owner=sender,
    #     nonce=sender.nonce,
    #     contract=contract,
    #     receiver=receiver,
    #     gas_limit=int(args.gas_limit),
    #     gas_price=int(args.gas_price),
    #     version=int(args.version),
    #     options=int(args.options),
    #     should_prepare_args=should_prepare_args,
    #     guardian_and_relayer_data=guardian_and_relayer_data,
    #     native_token_amount=int(args.value),
    #     token_transfers=token_transfers,
    #     opt_gas_limit=opt_gas_limit,
    #     function=function,
    #     abi=contract_abi,
    #     arguments=arguments,
    # )

    # _send_or_simulate(tx, contract, args)


def _get_contract_arguments(args: Any) -> tuple[list[Any], bool]:
    json_args = json.loads(Path(args.arguments_file).expanduser().read_text()) if args.arguments_file else None

    if json_args and args.arguments:
        raise Exception("Provide either '--arguments' or '--arguments-file'.")

    if json_args:
        if not args.abi:
            raise Exception("Can't use '--arguments-file' without providing the Abi file.")

        return json_args, False
    else:
        return args.arguments, True


def _prepare_token_transfers(transfers: list[str]) -> list[TokenTransfer]:
    token_computer = TokenComputer()
    token_transfers: list[TokenTransfer] = []

    for i in range(0, len(transfers) - 1, 2):
        identifier = transfers[i]
        amount = int(transfers[i + 1])
        nonce = token_computer.extract_nonce_from_extended_identifier(identifier)

        token = Token(identifier, nonce)
        transfer = TokenTransfer(token, amount)
        token_transfers.append(transfer)

    return token_transfers


def _send_or_simulate(tx: Transaction, contract_address: Address, args: Any):
    output_builder = cli_shared.send_or_simulate(tx, args, dump_output=False)
    output_builder.set_contract_address(contract_address)
    utils.dump_out_json(output_builder.build(), outfile=args.outfile)
