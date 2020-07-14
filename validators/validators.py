import binascii
import json
import logging

from erdpy import errors
from erdpy.accounts import Address
from erdpy.config import (GAS_PER_DATA_BYTE, MIN_GAS_LIMIT,
                          MetaChainSystemSCsCost)
from os import path

from erdpy import guards
from erdpy.accounts import Address, Account
from erdpy.config import MIN_GAS_LIMIT, GAS_PER_DATA_BYTE, MetaChainSystemSCsCost
from erdpy.wallet.pem import parse_validator_pem
from erdpy.wallet.signing import sign_message_with_bls_key

logger = logging.getLogger("validators")

_STAKE_SMART_CONTRACT_ADDRESS = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"


def estimate_system_sc_call(args, base_cost, factor=1):
    num_bytes = len(args.data)
    gas_limit = MIN_GAS_LIMIT + num_bytes * GAS_PER_DATA_BYTE
    gas_limit += factor * base_cost
    return gas_limit


def _read_json_file(file_path):
    val_file = path.expanduser(file_path)
    guards.is_file(val_file)
    with open(file_path,  "r") as json_file:
        try:
            data = json.load(json_file)
        except Exception:
            raise Exception("cannot read validators data")
        return data


def parse_args_for_stake(args):
    validators_data_file = args.validators_data_file
    validators_data = _read_json_file(validators_data_file)

    reward_address = args.reward_address

    if args.pem:
        account = Account(pem_file=args.pem)
    elif args.keyfile and args.passfile:
        account = Account(key_file=args.keyfile, pass_file=args.passfile)

    num_of_nodes = len(validators_data["validators"])
    stake_data = 'stake@' + binascii.hexlify(num_of_nodes.to_bytes(1, byteorder="little")).decode()
    for validator in validators_data["validators"]:
        # get validator
        seed, bls_key = parse_validator_pem(validator["pemFilePath"])
        signed_message = sign_message_with_bls_key(account.address.pubkey().hex(), seed.hex())
        stake_data += f"@{bls_key}@{signed_message}"

    if reward_address:
        reward_address = Address(args.reward_address)
        stake_data += '@' + reward_address.hex()

    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS
    args.data = stake_data

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.STAKE, num_of_nodes)

    return args


def parse_args_for_un_stake(args):
    parsed_keys, num_keys = parse_keys(args.nodes_public_keys)
    args.data = 'unStake' + parsed_keys
    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.UNSTAKE, num_keys)

    return args


def parse_args_for_un_bond(args):
    parsed_keys, num_keys = parse_keys(args.nodes_public_keys)
    args.data = 'unBond' + parsed_keys
    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.UNBOND, num_keys)

    return args


def parse_args_for_un_jail(args):
    parsed_keys, num_keys = parse_keys(args.nodes_public_keys)
    args.data = 'unJail' + parsed_keys
    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.UNJAIL, num_keys)

    return args


def parse_args_for_changing_reward_address(args):
    reward_address = Address(args.reward_address)
    args.data = 'changeRewardAddress@' + reward_address.hex()
    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.CHANGE_REWARD_ADDRESS)

    return args


def parse_args_for_claim(args):
    args.data = 'claim'
    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.CLAIM)

    return args


def parse_keys(bls_public_keys):
    keys = bls_public_keys.split(',')
    parsed_keys = ''
    for key in keys:
        parsed_keys += '@' + key
    return parsed_keys, len(keys)


def convert_to_hex(key):
    return binascii.hexlify(bytes(key, 'utf-8')).decode()
