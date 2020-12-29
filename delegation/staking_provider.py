import binascii
from typing import Any
from os import path

from erdpy.accounts import Account
from erdpy.config import MetaChainSystemSCsCost
from erdpy.utils import read_json_file_validators, parse_keys
from erdpy.validators.core import estimate_system_sc_call
from erdpy.wallet.pem import parse_validator_pem
from erdpy.wallet.signing import sign_message_with_bls_key

DELEGATION_MANAGER_SC_ADDRESS = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqylllslmq6y6"


def prepare_args_for_create_new_staking_contract(args: Any):
    args.data = 'createNewDelegationContract'
    args.data += '@' + string_to_hex_bytes(str(args.total_delegation_cap))
    args.data += '@' + string_to_hex_bytes(str(args.service_fee))

    args.receiver = DELEGATION_MANAGER_SC_ADDRESS

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.DELEGATION_MGR_OPS, 3)


def string_to_hex_bytes(number_str: str) -> str:
    num_of_bytes = 1
    if len(number_str) > 2:
        num_of_bytes = int(len(number_str) / 2)
    int_str = int(number_str)
    int_bytes = int_str.to_bytes(num_of_bytes, byteorder="big")
    bytes_str = binascii.hexlify(int_bytes).decode()
    return bytes_str


def prepare_args_for_add_nodes(args: Any):
    validators_file = args.validators_file
    validators_data = read_json_file_validators(validators_file)

    # TODO: Refactor, so that only address is received here.
    if args.pem:
        account = Account(pem_file=args.pem)
    elif args.keyfile and args.passfile:
        account = Account(key_file=args.keyfile, pass_file=args.passfile)

    add_nodes_data = "addNodes"
    num_of_nodes = len(validators_data.get("validators", []))
    for validator in validators_data.get("validators", []):
        # get validator
        validator_pem = validator.get("pemFile")
        validator_pem = path.join(path.dirname(validators_file), validator_pem)
        seed, bls_key = parse_validator_pem(validator_pem)
        print(bls_key)
        signed_message = sign_message_with_bls_key(account.address.pubkey().hex(), seed.hex())
        add_nodes_data += f"@{bls_key}@{signed_message}"

    args.receiver = args.delegation_contract
    args.data = add_nodes_data
    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.DELEGATION_OPS, num_of_nodes + 1)


def prepare_args_for_remove_nodes(args: Any):
    _prepare_args("removeNodes", args)


def prepare_args_for_stake_nodes(args: Any):
    parsed_keys, num_keys = parse_keys(args.bls_keys)
    args.data = 'stakeNodes' + parsed_keys
    args.receiver = args.delegation_contract

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.DELEGATION_OPS
                                                 + MetaChainSystemSCsCost.STAKE, num_keys + 1)


def prepare_args_for_unbond_nodes(args: Any):
    parsed_keys, num_keys = parse_keys(args.bls_keys)
    args.data = 'unBondNodes' + parsed_keys
    args.receiver = args.delegation_contract

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.DELEGATION_OPS
                                                 + MetaChainSystemSCsCost.UNBOND, num_keys + 1)


def prepare_args_for_unstake_nodes(args: Any):
    parsed_keys, num_keys = parse_keys(args.bls_keys)
    args.data = 'unStakeNodes' + parsed_keys
    args.receiver = args.delegation_contract

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.DELEGATION_OPS
                                                 + MetaChainSystemSCsCost.UNSTAKE, num_keys + 1)


def prepare_args_for_unjail_nodes(args: Any):
    _prepare_args("unjail", args)


def _prepare_args(command: str, args: Any):
    parsed_keys, num_keys = parse_keys(args.bls_keys)
    args.data = command + parsed_keys
    args.receiver = args.delegation_contract

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.DELEGATION_OPS, num_keys + 1)


def prepare_args_change_service_fee(args: Any):
    data = 'changeServiceFee'
    data += '@' + string_to_hex_bytes(str(args.service_fee))

    args.data = data
    args.receiver = args.delegation_contract
    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.DELEGATION_OPS, 1)


def prepare_args_modify_delegation_cap(args: Any):
    data = 'modifyTotalDelegationCap'
    data += '@' + string_to_hex_bytes(str(args.delegation_cap))

    args.data = data
    args.receiver = args.delegation_contract
    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.DELEGATION_OPS, 1)


def prepare_args_automatic_activation(args: Any):
    data = 'setAutomaticActivation'
    if args.set:
        data += '@' + binascii.hexlify(str.encode('yes')).decode()

    if args.unset:
        data += '@' + binascii.hexlify(str.encode('no')).decode()

    args.data = data
    args.receiver = args.delegation_contract
    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.DELEGATION_OPS, 1)
