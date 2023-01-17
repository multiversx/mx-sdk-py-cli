from typing import Any, Dict, Protocol
from multiversx_sdk_cli.utils import ISerializable


class IAddress:
    def hex(self) -> str:
        return ""

    def bech32(self) -> str:
        return ""

    def pubkey(self) -> bytes:
        return bytes()


class ITransaction(ISerializable):
    def serialize(self) -> bytes:
        return bytes()

    def serialize_as_inner(self) -> str:
        return ''

    def to_dictionary(self) -> Dict[str, Any]:
        return {}

    def to_dictionary_as_inner(self) -> Dict[str, Any]:
        return {}

    def set_version(self, version: int):
        return

    def set_options(self, options: int):
        return

    def get_hash(self) -> str:
        return ""

    def get_data(self) -> str:
        return ""


class IAccount(Protocol):
    def sign_transaction(self, transaction: ITransaction) -> str:
        ...


class ISimulateResponse(Protocol):
    def to_dictionary(self) -> Dict[str, Any]:
        ...
