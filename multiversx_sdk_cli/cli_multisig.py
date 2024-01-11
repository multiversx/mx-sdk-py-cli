import logging
from typing import Any, List

from multiversx_sdk_core import Address
from multiversx_sdk_core.transaction_factories.transactions_factory_config import \
    TransactionsFactoryConfig

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.contracts import SmartContract
from multiversx_sdk_cli.errors import BadUsage
from multiversx_sdk_cli.transactions import compute_relayed_v1_data

logger = logging.getLogger("cli.multisig")

MULTISIG_SIGN_ACTION_FUNCTION = "sign"
MULTISIG_PERFORM_ACTION_FUNCTION = "performAction"


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "multisig", "Interact with a multisig smart contract")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "multisig", "sign", f"Sign a proposed action.")
    cli_shared.add_multisig_address_arg(sub)
    cli_shared.add_multisig_view_address_arg(sub)
    cli_shared.add_sign_multisig_action_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)

    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=sign_action)

    sub = cli_shared.add_command_subparser(subparsers, "multisig", "perform-action", f"Perform an action that has reached quorum.")
    cli_shared.add_multisig_address_arg(sub)
    cli_shared.add_multisig_view_address_arg(sub)
    cli_shared.add_sign_multisig_action_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_guardian=True)

    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    sub.add_argument("--wait-result", action="store_true", default=False,
                     help="signal to wait for the transaction result - only valid if --send is set")
    sub.add_argument("--timeout", default=100, help="max num of seconds to wait for result"
                                                    " - only valid if --wait-result is set")
    sub.set_defaults(func=perform_action)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def sign_action(args: Any):
    args = utils.as_object(args)

    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)

    sender = cli_shared.prepare_account(args)
    contract_address = Address.new_from_bech32(args.multisig)

    action_id = args.action_id
    if action_id == "all":
        raise BadUsage("`all` is not supported at the moment. Please use a specific action id")

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=contract_address,
        function=MULTISIG_SIGN_ACTION_FUNCTION,
        arguments=args.action_id,
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        transfers=None,
        nonce=int(args.nonce),
        version=int(args.version),
        options=int(args.options),
        guardian=args.guardian)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)


def perform_action(args: Any):
    args = utils.as_object(args)

    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    cli_shared.prepare_nonce_in_args(args)

    config = TransactionsFactoryConfig(args.chain)
    contract = SmartContract(config)

    sender = cli_shared.prepare_account(args)
    contract_address = Address.new_from_bech32(args.multisig)

    action_id = args.action_id
    if action_id == "all":
        raise BadUsage("`all` is not supported at the moment. Please use a specific action id")

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=contract_address,
        function=MULTISIG_PERFORM_ACTION_FUNCTION,
        arguments=args.action_id,
        gas_limit=int(args.gas_limit),
        value=int(args.value),
        transfers=None,
        nonce=int(args.nonce),
        version=int(args.version),
        options=int(args.options),
        guardian=args.guardian)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

    cli_shared.send_or_simulate(tx, args)
