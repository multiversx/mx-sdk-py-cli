from erdpy.accounts import Address
from erdpy.contracts import SmartContract
from erdpy.testnet import wallets


def get_owner_of_genesis_contracts():
    users = wallets.get_users()
    return users["alice"]


def get_delegation_address() -> Address:
    contract = SmartContract()
    contract.owner = get_owner_of_genesis_contracts()
    contract.owner.nonce = 0
    contract.compute_address()
    return contract.address


def is_last_user(nickname: str) -> bool:
    return nickname == "mike"


def is_foundational_node(nickname: str) -> bool:
    return nickname == "validator00"
