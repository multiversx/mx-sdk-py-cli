
from typing import Any, Dict, List, Tuple


class IAddress:
    def hex(self) -> str:
        return ""

    def bech32(self) -> str:
        return ""

    def pubkey(self) -> bytes:
        return bytes()


class IAccount:
    def get_seed(self) -> bytes:
        return bytes()


class ITransaction:
    def serialize(self) -> bytes:
        return bytes()

    def to_dictionary(self) -> Dict[str, Any]:
        return {}

    def to_dictionary_as_inner(self) -> Dict[str, Any]:
        return {}


class IElrondProxy:
    def get_account_nonce(self, address: IAddress) -> int:
        return 0

    def send_transaction(self, payload: Any) -> str:
        return ""

    def send_transactions(self, payload: List[Any]) -> Tuple[int, List[str]]:
        return 0, []
