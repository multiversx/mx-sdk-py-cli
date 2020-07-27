
from typing import Any, Dict, List, Tuple


class IAccount:
    def get_seed(self) -> bytes:
        return bytes()


class ITransaction:
    def serialize(self) -> bytes:
        return bytes()

    def to_dictionary(self) -> Dict[str, Any]:
        return {}


class IElrondProxy:
    def send_transaction(self, payload: Any) -> str:
        return ""

    def send_transactions(self, payload: List[Any]) -> Tuple[int, List[str]]:
        return 0, []
