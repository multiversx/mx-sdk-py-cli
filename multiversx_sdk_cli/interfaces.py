from typing import Any, Dict, Protocol


class IAddress(Protocol):
    def to_hex(self) -> str:
        ...

    def to_bech32(self) -> str:
        ...


ITransactionOptions = int
ITransactionVersion = int
ISignature = bytes


class ITransactionPayload(Protocol):
    data: bytes
    def encoded(self) -> str: ...
    def length(self) -> int: ...


class ITransaction(Protocol):
    version: ITransactionVersion
    options: ITransactionOptions
    signature: ISignature
    guardian_signature: ISignature

    @property
    def data(self) -> ITransactionPayload:
        ...

    def serialize_for_signing(self) -> bytes:
        ...

    def to_dictionary(self, with_signature: bool = True) -> Dict[str, Any]:
        ...


class IAccount(Protocol):
    def sign_transaction(self, transaction: ITransaction) -> str:
        ...


class ISimulateResponse(Protocol):
    def to_dictionary(self) -> Dict[str, Any]:
        ...
