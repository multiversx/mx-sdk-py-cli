from typing import Any, Dict, List

from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.localnet import wallets
from multiversx_sdk_cli.localnet.config_root import ConfigRoot
from multiversx_sdk_cli.localnet.genesis import is_last_user

ENTIRE_SUPPLY = 20000000000000000000000000
# For localnet, we delegate for 1 node
DELEGATED_VALUE = 2500000000000000000000


def build(config: ConfigRoot) -> List[Any]:
    num_validators = config.num_all_validators()
    genesis_items: List[Dict[str, Any]] = []
    remaining_supply = ENTIRE_SUPPLY

    for nickname, account in wallets.get_validator_wallets(num_validators).items():
        value = 2500000000000000000000
        entry = _build_validator_entry(nickname, account, value)
        genesis_items.append(entry)
        remaining_supply -= value

    for nickname, account in wallets.get_users().items():
        # The last user (mike) gets all remaining tokens
        value = remaining_supply if is_last_user(nickname) else 100000000000000000000000
        entry = _build_user_entry(nickname, account, value)
        genesis_items.append(entry)
        remaining_supply -= value

    return genesis_items


def _build_validator_entry(nickname: str, account: Account, value: int) -> Dict[str, Any]:
    return {
        "nickname": nickname,
        "address": account.address.to_bech32(),
        "supply": str(value),
        "balance": "0",
        "stakingvalue": str(value)
    }


def _build_user_entry(nickname: str, account: Account, value: int) -> Dict[str, Any]:
    return {
        "nickname": nickname,
        "address": account.address.to_bech32(),
        "supply": str(value),
        "balance": str(value),
        "stakingvalue": "0"
    }
