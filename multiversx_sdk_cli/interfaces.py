from typing import Any, Dict, Protocol

from multiversx_sdk import Address, Transaction


# fmt: off
class ITransaction(Protocol):
    sender: str
    receiver: str
    gas_limit: int
    chain_id: str
    nonce: int
    value: int
    sender_username: str
    receiver_username: str
    gas_price: int
    data: bytes
    version: int
    options: int
    guardian: str
    signature: bytes
    guardian_signature: bytes
    relayer: str
    relayer_signature: bytes


class IAccount(Protocol):
    use_hash_signing: bool
    address: Address

    def sign_transaction(self, transaction: Transaction) -> bytes:
        ...


class ISimulateResponse(Protocol):
    def to_dictionary(self) -> Dict[str, Any]:
        ...
