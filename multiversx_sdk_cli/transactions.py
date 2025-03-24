import json
import logging
from typing import Any, Optional, Protocol, TextIO, Union

from multiversx_sdk import (
    Address,
    AwaitingOptions,
    SmartContractResult,
    TokenTransfer,
    Transaction,
    TransactionEvent,
    TransactionLogs,
    TransactionOnNetwork,
    TransactionsFactoryConfig,
    TransferTransactionsFactory,
)

from multiversx_sdk_cli import errors
from multiversx_sdk_cli.base_transactions_controller import BaseTransactionsController
from multiversx_sdk_cli.constants import MIN_GAS_LIMIT
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.interfaces import IAccount

logger = logging.getLogger("transactions")


ONE_SECOND_IN_MILLISECONDS = 1000


# fmt: off
class INetworkProvider(Protocol):
    def send_transaction(self, transaction: Transaction) -> bytes:
        ...

    def get_transaction(self, transaction_hash: Union[bytes, str]) -> TransactionOnNetwork:
        ...

    def await_transaction_completed(self, transaction_hash: Union[bytes, str], options: Optional[AwaitingOptions] = None) -> TransactionOnNetwork:
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
        guardian_and_relayer_data: GuardianRelayerData,
        token_transfers: Optional[list[TokenTransfer]] = None,
        data: Optional[str] = None,
    ) -> Transaction:
        # if no value, token transfers or data provided, create plain transaction
        if not native_amount and not token_transfers and not data:
            transaction = Transaction(
                sender=sender.address,
                receiver=receiver,
                gas_limit=MIN_GAS_LIMIT,
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

        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction


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


def transaction_event_to_dictionary(event: TransactionEvent) -> dict[str, Any]:
    return {
        "address": event.address.to_bech32(),
        "identifier": event.identifier,
        "topics": [topic.hex() for topic in event.topics],
        "data": event.data.decode(),
        "additional_data": [data.hex() for data in event.additional_data],
    }


def transaction_logs_to_dictionary(logs: TransactionLogs) -> dict[str, Any]:
    return {
        "address": logs.address.to_bech32(),
        "events": [transaction_event_to_dictionary(event) for event in logs.events],
    }


def smart_contract_result_to_dictionary(result: SmartContractResult) -> dict[str, Any]:
    return {
        "sender": result.sender.to_bech32(),
        "receiver": result.receiver.to_bech32(),
        "data": result.data.decode(),
        "logs": transaction_logs_to_dictionary(result.logs),
    }


def transaction_on_network_to_dictionary(tx: TransactionOnNetwork) -> dict[str, Any]:
    return {
        "sender": tx.sender.to_bech32(),
        "receiver": tx.receiver.to_bech32(),
        "hash": tx.hash.hex(),
        "nonce": tx.nonce,
        "round": tx.round,
        "epoch": tx.epoch,
        "timestamp": tx.timestamp,
        "blockHash": tx.block_hash.hex(),
        "miniBlockHash": tx.miniblock_hash.hex(),
        "senderShard": tx.sender_shard,
        "receiverShard": tx.receiver_shard,
        "value": tx.value,
        "gasLimit": tx.gas_limit,
        "gasPrice": tx.gas_price,
        "function": tx.function,
        "data": tx.data.decode(),
        "version": tx.version,
        "options": tx.options,
        "signature": tx.signature.hex(),
        "status": tx.status.status,
        "smartContractResults": [smart_contract_result_to_dictionary(res) for res in tx.smart_contract_results],
        "logs": transaction_logs_to_dictionary(tx.logs),
    }
