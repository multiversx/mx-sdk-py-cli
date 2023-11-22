from multiversx_sdk_core.address import Address, AddressComputer

from multiversx_sdk_cli.contracts import SmartContract
from multiversx_sdk_cli.localnet import wallets


def get_owner_of_genesis_contracts():
    users = wallets.get_users()
    return users["alice"]


def get_delegation_address() -> Address:
    contract = SmartContract()
    contract.owner = get_owner_of_genesis_contracts()
    contract.owner.nonce = 0

    address_computer = AddressComputer()
    contract.address = address_computer.compute_contract_address(contract.owner.address, contract.owner.nonce)
    return contract.address


def is_last_user(nickname: str) -> bool:
    return nickname == "mike"


def is_foundational_node(nickname: str) -> bool:
    return nickname == "validator00"
