from typing import Any, Dict, Protocol


class IAddress(Protocol):
    def to_hex(self) -> str:
        ...

    def to_bech32(self) -> str:
        ...


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


class IAccount(Protocol):
    def sign_transaction(self, transaction: ITransaction) -> str:
        ...


class ISimulateResponse(Protocol):
    def to_dictionary(self) -> Dict[str, Any]:
        ...
