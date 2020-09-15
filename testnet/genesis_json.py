
from typing import List

from erdpy.accounts import Account
from erdpy.testnet import wallets
from erdpy.testnet.config import TestnetConfiguration

ENTIRE_SUPPLY = 20000000000000000000000000


def build(testnet_config: TestnetConfiguration) -> List[any]:
    num_validators = testnet_config.num_all_validators()
    genesis = []
    remaining_supply = ENTIRE_SUPPLY

    for nickname, account in wallets.get_validator_wallets(num_validators).items():
        value = 2500000000000000000000
        entry = _build_validator_entry(nickname, account, value)
        genesis.append(entry)
        remaining_supply -= value

    for nickname, account in wallets.get_users().items():
        # The last user (mike) gets all remaining tokens
        value = remaining_supply if nickname == "mike" else 10000000000000000000000
        entry = _build_user_entry(nickname, account, value)
        genesis.append(entry)
        remaining_supply -= value

    return genesis


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


def _build_user_entry(nickname: str, account: Account, value: int):
    return {
        "nickname": nickname,
        "address": account.address.bech32(),
        "supply": str(value),
        "balance": str(value),
        "stakingvalue": "0",
        "delegation": {
            "address": "",
            "value": "0"
        }
    }
