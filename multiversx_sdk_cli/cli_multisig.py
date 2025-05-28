import json
import logging
from pathlib import Path
from typing import Any

from multiversx_sdk import (
    Action,
    ActionFullInfo,
    AddBoardMember,
    AddProposer,
    Address,
    AddressComputer,
    CallActionData,
    ChangeQuorum,
    EsdtTokenPayment,
    EsdtTransferExecuteData,
    MultisigController,
    ProxyNetworkProvider,
    RemoveUser,
    SCDeployFromSource,
    SCUpgradeFromSource,
    SendAsyncCall,
    SendTransferExecuteEgld,
    SendTransferExecuteEsdt,
    Transaction,
    TransactionsFactoryConfig,
)
from multiversx_sdk.abi import Abi

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.args_validation import (
    ensure_wallet_args_are_provided,
    validate_broadcast_args,
    validate_chain_id_args,
    validate_proxy_argument,
    validate_transaction_args,
)
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.config import get_config_for_network_providers
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
    cli_shared.add_metadata_arg(sub)
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
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

    sub.add_argument("--contract-to-copy", required=True, type=str, help="the bech32 address of the contract to copy")
    sub.add_argument("--contract-abi", type=str, help="the ABI file of the contract to copy")
    _add_arguments_arg(sub)
    cli_shared.add_metadata_arg(sub)
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=deploy_from_source)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "upgrade-from-source",
        f"Propose a smart contract upgrade from a previously deployed smart contract.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)

    sub.add_argument(
        "--contract-to-upgrade", required=True, type=str, help="the bech32 address of the contract to upgrade"
    )
    sub.add_argument("--contract-to-copy", required=True, type=str, help="the bech32 address of the contract to copy")
    sub.add_argument("--contract-abi", type=str, help="the ABI file of the contract to copy")
    _add_arguments_arg(sub)
    cli_shared.add_metadata_arg(sub)
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=upgrade_from_source)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "sign-action",
        f"Sign a proposed action.{output_description}",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=sign_action)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "sign-batch",
        f"Sign a batch of actions.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)

    sub.add_argument("--batch", required=True, type=int, help="the id of the batch to sign")
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=sign_batch)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "sign-and-perform",
        f"Sign a proposed action and perform it. Works only if quorum is reached.{output_description}",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=sign_and_perform)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "sign-batch-and-perform",
        f"Sign a batch of actions and perform them. Works only if quorum is reached.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)

    sub.add_argument("--batch", required=True, type=int, help="the id of the batch to sign")
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=sign_batch_and_perform)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "unsign-action",
        f"Unsign a proposed action.{output_description}",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=unsign_action)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "unsign-batch",
        f"Unsign a batch of actions.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)

    sub.add_argument("--batch", required=True, type=int, help="the id of the batch to sign")
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=unsign_batch)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "unsign-for-outdated-members",
        f"Unsign an action for outdated board members.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)

    _add_action_id_arg(sub)
    sub.add_argument(
        "--outdated-members",
        nargs="+",
        type=int,
        help="IDs of the outdated board members",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=unsign_for_outdated_board_members)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "perform-action",
        f"Perform an action that has reached quorum.{output_description}",
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=perform_action)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "perform-batch",
        f"Perform a batch of actions that has reached quorum.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)

    sub.add_argument("--batch", required=True, type=int, help="the id of the batch to sign")
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
        help="max num of seconds to wait for result - only valid if --wait-result is set",
    )
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)

    sub.set_defaults(func=perform_batch)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-quorum",
        f"Perform a smart contract query to get the quorum.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_quorum)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-num-board-members",
        f"Perform a smart contract query to get the number of board members.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_num_board_members)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-num-groups",
        f"Perform a smart contract query to get the number of groups.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_num_groups)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-num-proposers",
        f"Perform a smart contract query to get the number of proposers.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_num_proposers)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-action-group",
        f"Perform a smart contract query to get the actions in a group.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    sub.add_argument("--group", required=True, type=int, help="the group id")
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_action_group)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-last-action-group-id",
        f"Perform a smart contract query to get the id of the last action in a group.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_last_group_action_id)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-action-last-index",
        f"Perform a smart contract query to get the index of the last action.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_action_last_index)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "is-signed-by",
        f"Perform a smart contract query to check if an action is signed by a user.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    _add_action_id_arg(sub)
    sub.add_argument("--user", required=True, type=str, help="the bech32 address of the user")
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=is_signed_by)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "is-quorum-reached",
        f"Perform a smart contract query to check if an action has reached quorum.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    _add_action_id_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=is_quorum_reached)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-pending-actions",
        f"Perform a smart contract query to get the pending actions full info.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_pending_actions_full_info)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-user-role",
        f"Perform a smart contract query to get the role of a user.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    sub.add_argument("--user", required=True, type=str, help="the bech32 address of the user")
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_user_role)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-board-members",
        f"Perform a smart contract query to get all the board members.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_all_board_members)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-proposers",
        f"Perform a smart contract query to get all the proposers.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_all_proposers)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-action-data",
        f"Perform a smart contract query to get the data of an action.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    _add_action_id_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_action_data)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-action-signers",
        f"Perform a smart contract query to get the signers of an action.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    _add_action_id_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_action_signers)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-action-signers-count",
        f"Perform a smart contract query to get the number of signers of an action.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    _add_action_id_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_action_signer_count)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "get-action-valid-signers-count",
        f"Perform a smart contract query to get the number of valid signers of an action.{output_description}",
    )
    _add_contract_arg(sub)
    _add_abi_arg(sub)
    _add_action_id_arg(sub)
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_action_valid_signer_count)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "multisig",
        "parse-propose-action",
        f"Parses the propose action transaction to extract proposal ID.{output_description}",
    )
    _add_abi_arg(sub)
    sub.add_argument("--hash", required=True, type=str, help="the transaction hash of the propose action")
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=parse_proposal)

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

    token_transfers = args.token_transfers or None
    if token_transfers:
        token_transfers = cli_shared.prepare_token_transfers(token_transfers)

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
        should_prepare_args_for_factory=should_prepare_args,
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

    if not args.token_transfers:
        raise Exception("Token transfers not provided.")

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
    token_transfers = cli_shared.prepare_token_transfers(args.token_transfers)

    tx = multisig.prepare_transfer_execute_esdt_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        receiver=receiver,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        should_prepare_args_for_factory=should_prepare_args,
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

    token_transfers = args.token_transfers or None
    if token_transfers:
        token_transfers = cli_shared.prepare_token_transfers(args.token_transfers)

    tx = multisig.prepare_async_call_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        receiver=receiver,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        should_prepare_args_for_factory=should_prepare_args,
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
    contract_to_copy = Address.new_from_bech32(args.contract_to_copy)

    contract_abi = Abi.load(Path(args.contract_abi)) if args.contract_abi else None
    arguments, should_prepare_args = _get_contract_arguments(args)

    tx = multisig.prepare_contract_deploy_from_source_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        contract_to_copy=contract_to_copy,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        upgradeable=args.metadata_upgradeable,
        readable=args.metadata_readable,
        payable=args.metadata_payable,
        payable_by_sc=args.metadata_payable_by_sc,
        should_prepare_args_for_factory=should_prepare_args,
        guardian_and_relayer_data=guardian_and_relayer_data,
        native_token_amount=int(args.value),
        abi=contract_abi,
        arguments=arguments,
    )

    _send_or_simulate(tx, contract, args)


def upgrade_from_source(args: Any):
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
    contract_to_upgrade = Address.new_from_bech32(args.contract_to_upgrade)
    contract_to_copy = Address.new_from_bech32(args.contract_to_copy)

    contract_abi = Abi.load(Path(args.contract_abi)) if args.contract_abi else None
    arguments, should_prepare_args = _get_contract_arguments(args)

    tx = multisig.prepare_contract_upgrade_from_source_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        contract_to_upgrade=contract_to_upgrade,
        contract_to_copy=contract_to_copy,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        upgradeable=args.metadata_upgradeable,
        readable=args.metadata_readable,
        payable=args.metadata_payable,
        payable_by_sc=args.metadata_payable_by_sc,
        should_prepare_args_for_factory=should_prepare_args,
        guardian_and_relayer_data=guardian_and_relayer_data,
        native_token_amount=int(args.value),
        abi=contract_abi,
        arguments=arguments,
    )

    _send_or_simulate(tx, contract, args)


def sign_action(args: Any):
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

    tx = multisig.prepare_sign_action_transaction(
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


def sign_batch(args: Any):
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
    batch_id = int(args.batch)

    tx = multisig.prepare_sign_batch_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        batch_id=batch_id,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def sign_and_perform(args: Any):
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

    tx = multisig.prepare_sign_and_perform_transaction(
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


def sign_batch_and_perform(args: Any):
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
    batch_id = int(args.batch)

    tx = multisig.prepare_sign_batch_and_perform_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        batch_id=batch_id,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def unsign_action(args: Any):
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

    tx = multisig.prepare_unsign_action_transaction(
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


def unsign_batch(args: Any):
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
    batch_id = int(args.batch)

    tx = multisig.prepare_unsign_batch_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        batch_id=batch_id,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def unsign_for_outdated_board_members(args: Any):
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

    tx = multisig.prepare_unsign_for_outdated_board_members_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        action_id=action_id,
        outdated_board_members=args.outdated_members,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def perform_action(args: Any):
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

    tx = multisig.prepare_perform_action_transaction(
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


def perform_batch(args: Any):
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
    batch_id = int(args.batch)

    tx = multisig.prepare_perform_batch_transaction(
        owner=sender,
        nonce=sender.nonce,
        contract=contract,
        batch_id=batch_id,
        gas_limit=int(args.gas_limit),
        gas_price=int(args.gas_price),
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    _send_or_simulate(tx, contract, args)


def get_quorum(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    quorum = multisig.get_quorum(Address.new_from_bech32(args.contract))
    print(f"Quorum: {quorum}")


def get_num_board_members(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    num_board_members = multisig.get_num_board_members(Address.new_from_bech32(args.contract))
    print(f"Number of board members: {num_board_members}")


def get_num_groups(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    num_groups = multisig.get_num_groups(Address.new_from_bech32(args.contract))
    print(f"Number of groups: {num_groups}")


def get_num_proposers(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    num_proposers = multisig.get_num_proposers(Address.new_from_bech32(args.contract))
    print(f"Number of proposers: {num_proposers}")


def get_action_group(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    actions = multisig.get_action_group(Address.new_from_bech32(args.contract), args.group)
    print(f"Actions: [{actions}]")


def get_last_group_action_id(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    id = multisig.get_last_group_action_id(Address.new_from_bech32(args.contract))
    print(f"Last group action id: {id}")


def get_action_last_index(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    id = multisig.get_action_last_index(Address.new_from_bech32(args.contract))
    print(f"Action last index: {id}")


def is_signed_by(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    contract = Address.new_from_bech32(args.contract)
    action_id = int(args.action)
    user = Address.new_from_bech32(args.user)

    is_signed = multisig.is_signed_by(contract, user, action_id)
    print(f"Action {action_id} is signed by {user.to_bech32()}: {is_signed}")


def is_quorum_reached(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    contract = Address.new_from_bech32(args.contract)
    action_id = int(args.action)

    is_quorum_reached = multisig.is_quorum_reached(contract, action_id)
    print(f"Quorum reached for action {action_id}: {is_quorum_reached}")


def get_pending_actions_full_info(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    contract = Address.new_from_bech32(args.contract)

    controller = MultisigController(chain_id, proxy, abi)
    actions = controller.get_pending_actions_full_info(contract)

    output = [_convert_action_full_info_to_dict(action) for action in actions]
    utils.dump_out_json(output)


def get_user_role(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    contract = Address.new_from_bech32(args.contract)
    user = Address.new_from_bech32(args.user)

    role = multisig.get_user_role(contract, user)
    print(f"User {user.to_bech32()} has role: {role.name}")


def get_all_board_members(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    contract = Address.new_from_bech32(args.contract)

    board_members = multisig.get_all_board_members(contract)
    if not board_members:
        print(None)
    else:
        print("Board members:")
        for member in board_members:
            print(f" - {member.to_bech32()}")


def get_all_proposers(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    contract = Address.new_from_bech32(args.contract)

    proposers = multisig.get_all_proposers(contract)
    if not proposers:
        print(None)
    else:
        print("Proposers:")
        for proposer in proposers:
            print(f" - {proposer.to_bech32()}")


def get_action_data(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    controller = MultisigController(chain_id, proxy, abi)

    contract = Address.new_from_bech32(args.contract)
    action = args.action

    action_data = controller.get_action_data(contract=contract, action_id=action)
    utils.dump_out_json(_convert_action_to_dict(action_data))


def get_action_signers(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    contract = Address.new_from_bech32(args.contract)
    action = args.action

    signers = multisig.get_action_signers(contract, action)
    print(f"Signers for action {action}:")
    for signer in signers:
        print(f" - {signer.to_bech32()}")


def get_action_signer_count(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    contract = Address.new_from_bech32(args.contract)
    action = args.action

    signers = multisig.get_action_signer_count(contract, action)
    print(f"{signers} signers for action {action}:")


def get_action_valid_signer_count(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    contract = Address.new_from_bech32(args.contract)
    action = args.action

    signers = multisig.get_action_valid_signer_count(contract, action)
    print(f"{signers} valid signers for action {action}:")


def parse_proposal(args: Any):
    validate_proxy_argument(args)

    abi = Abi.load(Path(args.abi))
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    chain_id = proxy.get_network_config().chain_id
    multisig = MultisigController(chain_id, proxy, abi)

    id = multisig.await_completed_execute_propose_any(args.hash)
    print(f"Proposal ID: {id}")


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


def _send_or_simulate(tx: Transaction, contract_address: Address, args: Any):
    output_builder = cli_shared.send_or_simulate(tx, args, dump_output=False)
    output_builder.set_contract_address(contract_address)
    utils.dump_out_json(output_builder.build(), outfile=args.outfile)


def _convert_action_to_dict(action: Action) -> dict[str, Any]:
    if isinstance(action, AddBoardMember):
        return _convert_add_board_member_to_dict(action)
    elif isinstance(action, AddProposer):
        return _convert_add_proposer_to_dict(action)
    elif isinstance(action, RemoveUser):
        return _convert_remove_user_to_dict(action)
    elif isinstance(action, ChangeQuorum):
        return _convert_change_quorum_to_dict(action)
    elif isinstance(action, SendTransferExecuteEgld):
        return _convert_send_transfer_execute_egld_to_dict(action)
    elif isinstance(action, SendTransferExecuteEsdt):
        return _convert_send_transfer_execute_esdt_to_dict(action)
    elif isinstance(action, SendAsyncCall):
        return _convert_send_async_call_to_dict(action)
    elif isinstance(action, SCDeployFromSource):
        return _convert_sc_deploy_from_source_to_dict(action)
    elif isinstance(action, SCUpgradeFromSource):
        return _convert_sc_upgrade_from_source_to_dict(action)
    else:
        raise Exception(f"Unknown action type: {type(action)}")


def _convert_add_board_member_to_dict(action: AddBoardMember) -> dict[str, Any]:
    return {
        "type": "AddBoardMember",
        "discriminant": action.discriminant,
        "address": action.address.to_bech32(),
    }


def _convert_add_proposer_to_dict(action: AddProposer) -> dict[str, Any]:
    return {
        "type": "AddProposer",
        "discriminant": action.discriminant,
        "address": action.address.to_bech32(),
    }


def _convert_remove_user_to_dict(action: RemoveUser) -> dict[str, Any]:
    return {
        "type": "RemoveUser",
        "discriminant": action.discriminant,
        "address": action.address.to_bech32(),
    }


def _convert_change_quorum_to_dict(action: ChangeQuorum) -> dict[str, Any]:
    return {
        "type": "ChangeQuorum",
        "discriminant": action.discriminant,
        "quorum": action.quorum,
    }


def _convert_send_transfer_execute_egld_to_dict(action: SendTransferExecuteEgld) -> dict[str, Any]:
    return {
        "type": "SendTransferExecuteEgld",
        "discriminant": action.discriminant,
        "callActionData": _convert_call_action_data_to_dict(action.data),
    }


def _convert_call_action_data_to_dict(call_action_data: CallActionData) -> dict[str, Any]:
    return {
        "to": call_action_data.to.to_bech32(),
        "egldAmount": call_action_data.egld_amount,
        "optGasLimit": call_action_data.opt_gas_limit,
        "endpointName": call_action_data.endpoint_name,
        "arguments": [arg.hex() for arg in call_action_data.arguments],
    }


def _convert_send_transfer_execute_esdt_to_dict(action: SendTransferExecuteEsdt) -> dict[str, Any]:
    return {
        "type": "SendTransferExecuteEsdt",
        "discriminant": action.discriminant,
        "esdtTransferExecuteData": _convert_esdt_transfer_execute_data_to_dict(action.data),
    }


def _convert_esdt_transfer_execute_data_to_dict(call_action_data: EsdtTransferExecuteData) -> dict[str, Any]:
    return {
        "to": call_action_data.to.to_bech32(),
        "tokens": _convert_tokens_to_dict(call_action_data.tokens),
        "optGasLimit": call_action_data.opt_gas_limit,
        "endpointName": call_action_data.endpoint_name,
        "arguments": [arg.hex() for arg in call_action_data.arguments],
    }


def _convert_tokens_to_dict(tokens: list[EsdtTokenPayment]) -> list[dict[str, Any]]:
    return [
        {
            "tokenIdentifier": token.fields[0].get_payload(),
            "tokenNonce": token.fields[1].get_payload(),
            "amount": token.fields[2].get_payload(),
        }
        for token in tokens
    ]


def _convert_send_async_call_to_dict(action: SendAsyncCall) -> dict[str, Any]:
    return {
        "type": "SendAsyncCall",
        "discriminant": action.discriminant,
        "callActionData": _convert_call_action_data_to_dict(action.data),
    }


def _convert_sc_deploy_from_source_to_dict(action: SCDeployFromSource) -> dict[str, Any]:
    return {
        "type": "SCDeployFromSource",
        "discriminant": action.discriminant,
        "amount": action.amount,
        "source": action.source.to_bech32(),
        "codeMetadata": action.code_metadata.hex(),
        "arguments": [arg.hex() for arg in action.arguments],
    }


def _convert_sc_upgrade_from_source_to_dict(action: SCUpgradeFromSource) -> dict[str, Any]:
    return {
        "type": "SCDeployFromSource",
        "discriminant": action.discriminant,
        "scAddress": action.sc_address.to_bech32(),
        "amount": action.amount,
        "source": action.source.to_bech32(),
        "codeMetadata": action.code_metadata.hex(),
        "arguments": [arg.hex() for arg in action.arguments],
    }


def _convert_action_full_info_to_dict(action: ActionFullInfo) -> dict[str, Any]:
    return {
        "actionId": action.action_id,
        "groupId": action.group_id,
        "actionData": _convert_action_to_dict(action.action_data),
        "signers": [signer.to_bech32() for signer in action.signers],
    }
