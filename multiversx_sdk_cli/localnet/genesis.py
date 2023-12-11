from multiversx_sdk_core.address import Address, AddressComputer

from multiversx_sdk_cli.constants import NUMBER_OF_SHARDS
from multiversx_sdk_cli.localnet import wallets


def get_owner_of_genesis_contracts():
    users = wallets.get_users()
    return users["alice"]


def get_delegation_address() -> Address:
    owner = get_owner_of_genesis_contracts()
    owner.nonce = 0

    address_computer = AddressComputer(NUMBER_OF_SHARDS)
    address = address_computer.compute_contract_address(owner.address, owner.nonce)
    return address


def is_last_user(nickname: str) -> bool:
    return nickname == "mike"


def is_foundational_node(nickname: str) -> bool:
    return nickname == "validator00"
