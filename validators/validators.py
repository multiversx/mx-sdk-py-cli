import binascii
import logging

logger = logging.getLogger("validators")

_STAKE_SMART_CONTRACT_ADDRESS = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"


def parse_args_for_stake(args):
    num_of_nodes = int(args.number_of_nodes)
    keys = args.nodes_public_keys.split(',')
    if num_of_nodes != len(keys):
        logger.info("number of nodes is not equals with number of provided validators keys")
        return

    reward_address = args.reward_address

    stake_data = 'stake@' + binascii.hexlify(num_of_nodes.to_bytes(1, byteorder="little")).decode()
    for key in keys:
        stake_data += '@' + key + '@' + convert_to_hex('genesis')

    if reward_address:
        stake_data += '@' + convert_to_hex(reward_address)

    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS
    args.data = stake_data

    return args


def parse_args_for_un_stake(args):
    args.data = 'unStake' + parse_keys(args.nodes_public_keys)
    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS
    return args


def parse_args_for_un_bond(args):
    args.data = 'unBond' + parse_keys(args.nodes_public_keys)
    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS
    return args


def parse_args_for_un_jail(args):
    args.data = 'unJail' + parse_keys(args.nodes_public_keys)
    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS
    return args


def parse_args_for_changing_reward_address(args):
    args.data = 'changeRewardAddress@' + convert_to_hex(args.reward_address)
    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS
    return args


def parse_args_for_claim(args):
    args.data = 'claim'
    args.receiver = _STAKE_SMART_CONTRACT_ADDRESS
    return args


def parse_keys(bls_public_keys):
    keys = bls_public_keys.split(',')
    parsed_keys = ''
    for key in keys:
        parsed_keys += '@' + key
    return parsed_keys


def convert_to_hex(key):
    return binascii.hexlify(bytes(key, 'utf-8')).decode()
