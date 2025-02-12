import json
import logging
import time
from typing import Optional, Protocol, TextIO, Union

from multiversx_sdk import (
    Address,
    TokenTransfer,
    Transaction,
    TransactionOnNetwork,
    TransactionsFactoryConfig,
    TransferTransactionsFactory,
)

from multiversx_sdk_cli import errors
from multiversx_sdk_cli.base_transactions_controller import BaseTransactionsController
from multiversx_sdk_cli.interfaces import IAccount

logger = logging.getLogger("transactions")


# fmt: off
class INetworkProvider(Protocol):
    def send_transaction(self, transaction: Transaction) -> bytes:
        ...

    def get_transaction(self, transaction_hash: Union[bytes, str]) -> TransactionOnNetwork:
        ...
# fmt: on


class TransactionsController(BaseTransactionsController):
    def __init__(self, chain_id: str) -> None:
        config = TransactionsFactoryConfig(chain_id)
        self.factory = TransferTransactionsFactory(config)

    def create_transaction(
        self,
        sender: IAccount,
        receiver: Address,
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        token_transfers: Optional[list[TokenTransfer]] = None,
        data: Optional[str] = None,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        # if no value, token transfers or data provided, create plain transaction
        if not native_amount and not token_transfers and not data:
            transaction = Transaction(
                sender=sender.address,
                receiver=receiver,
                gas_limit=gas_limit,
                chain_id=self.factory.config.chain_id,
            )
        else:
            transaction = self.factory.create_transaction_for_transfer(
                sender=sender.address,
                receiver=receiver,
                native_amount=native_amount,
                token_transfers=token_transfers,
                data=data.encode() if data else None,
            )

        transaction.gas_limit = gas_limit
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_address
        transaction.relayer = relayer_address

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

        return transaction


def send_and_wait_for_result(transaction: Transaction, proxy: INetworkProvider, timeout: int) -> TransactionOnNetwork:
    if not transaction.signature:
        raise errors.TransactionIsNotSigned()

    txOnNetwork = _send_transaction_and_wait_for_result(proxy, transaction, timeout)
    return txOnNetwork


def _send_transaction_and_wait_for_result(
    proxy: INetworkProvider, payload: Transaction, num_seconds_timeout: int = 100
) -> TransactionOnNetwork:
    AWAIT_TRANSACTION_PERIOD = 5

    tx_hash = proxy.send_transaction(payload)
    num_periods_to_wait = int(num_seconds_timeout / AWAIT_TRANSACTION_PERIOD)

    for _ in range(0, num_periods_to_wait):
        time.sleep(AWAIT_TRANSACTION_PERIOD)

        tx = proxy.get_transaction(tx_hash)
        if tx.status.is_completed:
            return tx
        else:
            logger.info("Transaction not yet done.")

    raise errors.KnownError("Took too long to get transaction.")


def load_transaction_from_file(f: TextIO) -> Transaction:
    data_json: bytes = f.read().encode()
    transaction_dictionary = json.loads(data_json).get("tx") or json.loads(data_json).get("emittedTransaction")
    return Transaction.new_from_dictionary(transaction_dictionary)
