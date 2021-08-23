from typing import Any, List

from erdpy.accounts import Account, Address
from erdpy.testnet import wallets
from erdpy.testnet.config import TestnetConfiguration
from erdpy.testnet.genesis import (get_delegation_address,
                                   is_foundational_node, is_last_user)

ENTIRE_SUPPLY = 20000000000000000000000000
# For testnet, we delegate for 1 node
DELEGATED_VALUE = 2500000000000000000000


def build(testnet_config: TestnetConfiguration) -> List[Any]:
    num_validators = testnet_config.num_all_validators()
    genesis_items = []
    remaining_supply = ENTIRE_SUPPLY
    remaining_to_delegate = DELEGATED_VALUE
    delegation_address = get_delegation_address()

    for nickname, account in wallets.get_validator_wallets(num_validators).items():
        if is_foundational_node(nickname):
            continue

        value = 2500000000000000000000
        entry = _build_validator_entry(nickname, account, value)
        genesis_items.append(entry)
        remaining_supply -= value

    for nickname, account in wallets.get_users().items():
        # The last user (mike) gets all remaining tokens
        value = remaining_supply if is_last_user(nickname) else 100000000000000000000000
        delegated_value = remaining_to_delegate if is_last_user(nickname) else 100000000000000000000
        entry = _build_user_entry(nickname, account, value, delegated_value, delegation_address)
        genesis_items.append(entry)
        remaining_supply -= value
        remaining_to_delegate -= delegated_value

    return genesis_items


def _build_validator_entry(nickname: str, account: Account, value: int):
    return {
        "nickname": nickname,
        "address": account.address.bech32(),
        "supply": str(value),
        "balance": "0",
        "stakingvalue": str(value),
        "delegation": {
            "address": "",
            "value": "0"
        }
    }


def _build_user_entry(nickname: str, account: Account, value: int, delegated_value: int, delegation_address: Address):
    return {
        "nickname": nickname,
        "address": account.address.bech32(),
        "supply": str(value),
        "balance": str(value - delegated_value),
        "stakingvalue": "0",
        "delegation": {
            "address": delegation_address.bech32(),
            "value": str(delegated_value)
        }
    }
