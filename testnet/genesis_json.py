
from typing import List

from erdpy.accounts import Account
from erdpy.testnet import wallets
from erdpy.testnet.config import TestnetConfiguration


def build(testnet_config: TestnetConfiguration) -> List[any]:
    num_validators = testnet_config.num_all_validators()
    genesis = []

    for nickname, account in wallets.get_validator_wallets(num_validators).items():
        entry = _build_validator_entry(nickname, account)
        genesis.append(entry)

    for nickname, account in wallets.get_users().items():
        entry = _build_user_entry(nickname, account)
        genesis.append(entry)

    return genesis


def _build_validator_entry(nickname: str, account: Account):
    return {
        "nickname": nickname,
        "address": account.address.bech32(),
        "supply": "2500000000000000000000",
        "balance": "0",
        "stakingvalue": "2500000000000000000000",
        "delegation": {
            "address": "",
            "value": "0"
        }
    }


def _build_user_entry(nickname: str, account: Account):
    return {
        "nickname": nickname,
        "address": account.address.bech32(),
        "supply": "10000000000000000000000",
        "balance": "10000000000000000000000",
        "stakingvalue": "0",
        "delegation": {
            "address": "",
            "value": "0"
        }
    }
