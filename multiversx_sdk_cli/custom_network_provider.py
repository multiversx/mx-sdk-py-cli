from typing import Any, Dict, Optional, Protocol

from multiversx_sdk import GenericError, ProxyNetworkProvider

from multiversx_sdk_cli.errors import ProxyError
from multiversx_sdk_cli.interfaces import ISimulateResponse, ITransaction


class ITransactionOnNetwork(Protocol):
    hash: str
    is_completed: Optional[bool]

    def to_dictionary(self) -> Dict[str, Any]:
        ...


class CustomNetworkProvider:
    def __init__(self, url: str) -> None:
        self._provider = ProxyNetworkProvider(url)

    def send_transaction(self, transaction: ITransaction) -> str:
        try:
            hash = self._provider.send_transaction(transaction)
            return hash
        except GenericError as ge:
            url = ge.url
            message = ge.data.get("error", "")
            data = ge.data.get("data", "")
            code = ge.data.get("code", "")
            raise ProxyError(message, url, data, code)

    def get_transaction(self, tx_hash: str, with_process_status: Optional[bool] = False) -> ITransactionOnNetwork:
        return self._provider.get_transaction(tx_hash, with_process_status)

    def simulate_transaction(self, transaction: ITransaction) -> ISimulateResponse:
        return self._provider.simulate_transaction(transaction)
