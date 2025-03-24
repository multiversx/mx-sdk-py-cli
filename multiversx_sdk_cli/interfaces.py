from typing import Any, Protocol

from multiversx_sdk import Address, Transaction


# fmt: off
class IAccount(Protocol):
    address: Address

    def sign_transaction(self, transaction: Transaction) -> bytes:
        ...


class ISimulateResponse(Protocol):
    def to_dictionary(self) -> dict[str, Any]:
        ...
