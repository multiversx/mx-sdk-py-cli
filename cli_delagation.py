import binascii
import sys
from typing import Any

from erdpy import cli_shared, errors, utils
from erdpy.accounts import Address
from erdpy.delegation import staking_provider
from erdpy.proxy import ElrondProxy
from erdpy.transactions import do_prepare_transaction


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "staking-provider", "Staking provider omnitool")
    subparsers = parser.add_subparsers()

    # create new delegation contract
    sub = cli_shared.add_command_subparser(subparsers, "staking-provider", "create-new-delegation-contract",
                                           "Create a new delegation system smart contract, transferred value must be"
                                           "greater than baseIssuingCost + min deposit value")
    _add_common_arguments(sub)
    sub.add_argument("--total-delegation-cap", required=True, help="the total delegation contract capacity")
    sub.add_argument("--service-fee", required=True, help="the delegation contract service fee")
    sub.set_defaults(func=do_create_delegation_contract)

    # get contract address
    sub = cli_shared.add_command_subparser(subparsers, "staking-provider", "get-contract-address",
                                           "Get create contract address by transaction hash")
    sub.add_argument("--create-tx-hash", required=True, help="the hash")
    sub.add_argument("--sender", required=False, help="the sender address")
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_omit_fields_arg(sub)
    sub.set_defaults(func=get_contract_address_by_deploy_tx_hash)

    # add a new node
    sub = cli_shared.add_command_subparser(subparsers, "staking-provider", "add-nodes",
                                           "Add new nodes must be called by the contract owner")
    sub.add_argument("--validators-file", required=True, help="a JSON file describing the Nodes")
    sub.add_argument("--delegation-contract", required=True, help="address of the delegation contract")
    _add_common_arguments(sub)
    sub.set_defaults(func=add_new_nodes)

    # remove nodes
    sub = cli_shared.add_command_subparser(subparsers, "staking-provider", "remove-nodes",
                                           "Remove nodes must be called by the contract owner")
    sub.add_argument("--bls-keys", required=True, help="a list with the bls keys of the nodes")
    sub.add_argument("--delegation-contract", required=True, help="address of the delegation contract")
    _add_common_arguments(sub)
    sub.set_defaults(func=remove_nodes)

    # stake nodes
    sub = cli_shared.add_command_subparser(subparsers, "staking-provider", "stake-nodes",
                                           "Stake nodes must be called by the contract owner")
    sub.add_argument("--bls-keys", required=True, help="a list with the bls keys of the nodes")
    sub.add_argument("--delegation-contract", required=True, help="address of the delegation contract")
    _add_common_arguments(sub)
    sub.set_defaults(func=stake_nodes)

    # unbond nodes
    sub = cli_shared.add_command_subparser(subparsers, "staking-provider", "unbond-nodes",
                                           "Unbond nodes must be called by the contract owner")
    sub.add_argument("--bls-keys", required=True, help="a list with the bls keys of the nodes")
    sub.add_argument("--delegation-contract", required=True, help="address of the delegation contract")
    _add_common_arguments(sub)
    sub.set_defaults(func=unbond_nodes)

    # unstake nodes
    sub = cli_shared.add_command_subparser(subparsers, "staking-provider", "unstake-nodes",
                                           "Unstake nodes must be called by the contract owner")
    sub.add_argument("--bls-keys", required=True, help="a list with the bls keys of the nodes")
    sub.add_argument("--delegation-contract", required=True, help="address of the delegation contract")
    _add_common_arguments(sub)
    sub.set_defaults(func=unstake_nodes)

    # unjail nodes
    sub = cli_shared.add_command_subparser(subparsers, "staking-provider", "unjail-nodes",
                                           "Unjail nodes must be called by the contract owner")
    sub.add_argument("--bls-keys", required=True, help="a list with the bls keys of the nodes")
    sub.add_argument("--delegation-contract", required=True, help="address of the delegation contract")
    _add_common_arguments(sub)
    sub.set_defaults(func=unjail_nodes)

    # change service fee
    sub = cli_shared.add_command_subparser(subparsers, "staking-provider", "change-service-fee",
                                           "Change service fee must be called by the contract owner")
    sub.add_argument("--service-fee", required=True, help="new service fee value")
    sub.add_argument("--delegation-contract", required=True, help="address of the delegation contract")
    _add_common_arguments(sub)
    sub.set_defaults(func=change_service_fee)

    # modify total delegation cap
    sub = cli_shared.add_command_subparser(subparsers, "staking-provider", "modify-delegation-cap",
                                           "Modify delegation cap must be called by the contract owner")
    sub.add_argument("--delegation-cap", required=True, help="new delegation contract capacity")
    sub.add_argument("--delegation-contract", required=True, help="address of the delegation contract")
    _add_common_arguments(sub)
    sub.set_defaults(func=modify_delegation_cap)

    # set automatic activation
    sub = cli_shared.add_command_subparser(subparsers, "staking-provider", "automatic-activation",
                                           "Automatic activation must be called by the contract owner")

    sub.add_argument("--set", action="store_true", required=not (utils.is_arg_present("--unset", sys.argv)),
                     help="set automatic activation True")
    sub.add_argument("--unset", action="store_true", required=not (utils.is_arg_present("--set", sys.argv)),
                     help="set automatic activation False")

    sub.add_argument("--delegation-contract", required=True, help="address of the delegation contract")
    _add_common_arguments(sub)
    sub.set_defaults(func=automatic_activation)


def _add_common_arguments(sub: Any):
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_wallet_args(sub)
    cli_shared.add_tx_args(sub, with_receiver=False, with_data=False, with_estimate_gas=True)
    cli_shared.add_broadcast_args(sub, relay=False)
    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")


def do_create_delegation_contract(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    staking_provider.prepare_args_for_create_new_staking_contract(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def get_contract_address_by_deploy_tx_hash(args: Any):
    args = utils.as_object(args)
    omit_fields = cli_shared.parse_omit_fields_arg(args)

    proxy = ElrondProxy(args.proxy)

    transaction = proxy.get_transaction(args.create_tx_hash, with_results=True)
    utils.omit_fields(transaction, omit_fields)
    _get_sc_address_from_tx(transaction)


def add_new_nodes(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    staking_provider.prepare_args_for_add_nodes(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def remove_nodes(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    staking_provider.prepare_args_for_remove_nodes(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def stake_nodes(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    staking_provider.prepare_args_for_stake_nodes(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def unbond_nodes(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    staking_provider.prepare_args_for_unbond_nodes(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def unstake_nodes(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    staking_provider.prepare_args_for_unstake_nodes(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def unjail_nodes(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    staking_provider.prepare_args_for_unjail_nodes(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def change_service_fee(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    staking_provider.prepare_args_change_service_fee(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def modify_delegation_cap(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    staking_provider.prepare_args_modify_delegation_cap(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def automatic_activation(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    staking_provider.prepare_args_automatic_activation(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def _get_sc_address_from_tx(data: Any):
    if not isinstance(data, dict):
        raise errors.ProgrammingError("error")

    sc_results = data.get('smartContractResults')
    if sc_results is None:
        raise errors.ProgrammingError("smart contract results missing")

    # TODO improve robustness of this code in case of failed transaction
    try:
        sc_result = sc_results[0]
        data_field = sc_result['data']

        data_field_split = data_field.split('@')
        arg_1 = binascii.unhexlify(data_field_split[1])
        if not arg_1 == b'ok':
            raise errors.ProgrammingError(arg_1.decode("utf-8"))

        sc_address = binascii.unhexlify(data_field_split[2])
        address = Address(sc_address)
        print("Contract address: ", address)
    except Exception:
        raise errors.ProgrammingError(
            "cannot get the smart contract address from transaction results, please try again")
