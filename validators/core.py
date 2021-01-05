import binascii
import logging
from os import path
from typing import Any

from erdpy.validators.validators_file import ValidatorsFile
from erdpy.conv.conv import Converters
from erdpy.accounts import Account, Address
from erdpy.config import MetaChainSystemSCsCost, MIN_GAS_LIMIT, GAS_PER_DATA_BYTE
from erdpy.wallet.pem import parse_validator_pem
from erdpy.wallet.signing import sign_message_with_bls_key

logger = logging.getLogger("validators")

AUCTION_SMART_CONTRACT_ADDRESS = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"


def prepare_args_for_stake(args: Any):
    validators_file = ValidatorsFile(args.validators_file)

    reward_address = args.reward_address

    # TODO: Refactor, so that only address is received here.
    if args.pem:
        account = Account(pem_file=args.pem)
    elif args.keyfile and args.passfile:
        account = Account(key_file=args.keyfile, pass_file=args.passfile)

    num_of_nodes = validators_file.get_num_of_nodes()
    stake_data = 'stake@' + binascii.hexlify(num_of_nodes.to_bytes(1, byteorder="little")).decode()
    validators_list = validators_file.get_validators_list()
    for validator in validators_list:
        # get validator
        validator_pem = validator.get("pemFile")
        validator_pem = path.join(path.dirname(args.validators_file), validator_pem)
        seed, bls_key = parse_validator_pem(validator_pem)
        signed_message = sign_message_with_bls_key(account.address.pubkey().hex(), seed.hex())
        stake_data += f"@{bls_key}@{signed_message}"

    if reward_address:
        reward_address = Address(args.reward_address)
        stake_data += '@' + reward_address.hex()

    args.receiver = AUCTION_SMART_CONTRACT_ADDRESS
    args.data = stake_data

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.STAKE, num_of_nodes)


def prepare_args_for_unstake(args: Any):
    parsed_keys, num_keys = Converters.parse_keys(args.nodes_public_keys)
    args.data = 'unStake' + parsed_keys
    args.receiver = AUCTION_SMART_CONTRACT_ADDRESS

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.UNSTAKE, num_keys)


def prepare_args_for_unbond(args: Any):
    parsed_keys, num_keys = Converters.parse_keys(args.nodes_public_keys)
    args.data = 'unBond' + parsed_keys
    args.receiver = AUCTION_SMART_CONTRACT_ADDRESS

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.UNBOND, num_keys)


def prepare_args_for_unjail(args: Any):
    parsed_keys, num_keys = Converters.parse_keys(args.nodes_public_keys)
    args.data = 'unJail' + parsed_keys
    args.receiver = AUCTION_SMART_CONTRACT_ADDRESS

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.UNJAIL, num_keys)


def prepare_args_for_change_reward_address(args: Any):
    reward_address = Address(args.reward_address)
    args.data = 'changeRewardAddress@' + reward_address.hex()
    args.receiver = AUCTION_SMART_CONTRACT_ADDRESS

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.CHANGE_REWARD_ADDRESS)


def prepare_args_for_claim(args: Any):
    args.data = 'claim'
    args.receiver = AUCTION_SMART_CONTRACT_ADDRESS

    if args.estimate_gas:
        args.gas_limit = estimate_system_sc_call(args, MetaChainSystemSCsCost.CLAIM)


def estimate_system_sc_call(args, base_cost, factor=1):
    num_bytes = len(args.data)
    gas_limit = MIN_GAS_LIMIT + num_bytes * GAS_PER_DATA_BYTE
    gas_limit += factor * base_cost
    return gas_limit
