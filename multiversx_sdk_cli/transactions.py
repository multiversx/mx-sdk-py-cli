import json
import logging
from typing import Optional, Protocol, TextIO, Union

from multiversx_sdk import AwaitingOptions, Transaction, TransactionOnNetwork

from multiversx_sdk_cli import errors

logger = logging.getLogger("transactions")


ONE_SECOND_IN_MILLISECONDS = 1000


# fmt: off
class INetworkProvider(Protocol):
    def send_transaction(self, transaction: Transaction) -> bytes:
        ...

    def await_transaction_completed(self, transaction_hash: Union[bytes, str], options: Optional[AwaitingOptions] = None) -> TransactionOnNetwork:
        ...
# fmt: on


def send_and_wait_for_result(transaction: Transaction, proxy: INetworkProvider, timeout: int) -> TransactionOnNetwork:
    if not transaction.signature:
        raise errors.TransactionIsNotSigned()

    options = AwaitingOptions(timeout_in_milliseconds=timeout * ONE_SECOND_IN_MILLISECONDS)

    tx_hash = proxy.send_transaction(transaction)
    tx_on_network = proxy.await_transaction_completed(tx_hash, options)

    return tx_on_network


def load_transaction_from_file(f: TextIO) -> Transaction:
    data_json: bytes = f.read().encode()
    transaction_dictionary = json.loads(data_json).get("tx") or json.loads(data_json).get("emittedTransaction")
    return Transaction.new_from_dictionary(transaction_dictionary)
