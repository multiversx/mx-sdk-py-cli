from typing import Optional, Union

from multiversx_sdk import LedgerAccount, Transaction, TransactionComputer

from multiversx_sdk_cli.constants import (
    EXTRA_GAS_LIMIT_FOR_GUARDED_TRANSACTIONS,
    EXTRA_GAS_LIMIT_FOR_RELAYED_TRANSACTIONS,
)
from multiversx_sdk_cli.cosign_transaction import cosign_transaction
from multiversx_sdk_cli.interfaces import IAccount


class BaseTransactionsController:
    def __init__(self) -> None:
        pass

    def sign_transaction(
        self,
        transaction: Transaction,
        sender: Optional[IAccount] = None,
        guardian: Optional[IAccount] = None,
        relayer: Optional[IAccount] = None,
        guardian_service_url: Optional[str] = None,
        guardian_2fa_code: Optional[str] = None,
    ):
        """Signs the transaction using the sender's account and, if required, additionally signs with the guardian's and relayer's accounts. Ensures the appropriate transaction options are set as needed."""
        self._set_options_for_guarded_transaction_if_needed(transaction)
        self._set_options_for_hash_signing_if_needed(transaction, sender, guardian, relayer)

        if sender:
            transaction.signature = sender.sign_transaction(transaction)

        self._sign_guarded_transaction_if_guardian(
            transaction,
            guardian,
            guardian_service_url,
            guardian_2fa_code,
        )
        self._sign_relayed_transaction_if_relayer(transaction, relayer)

    def add_extra_gas_limit_if_required(self, transaction: Transaction):
        """In case of guarded or relayed transactions, extra gas limit is added."""
        if transaction.guardian:
            transaction.gas_limit += EXTRA_GAS_LIMIT_FOR_GUARDED_TRANSACTIONS

        if transaction.relayer:
            transaction.gas_limit += EXTRA_GAS_LIMIT_FOR_RELAYED_TRANSACTIONS

    def _set_options_for_guarded_transaction_if_needed(self, transaction: Transaction):
        if transaction.guardian:
            transaction_computer = TransactionComputer()
            transaction_computer.apply_guardian(transaction, transaction.guardian)

    def _set_options_for_hash_signing_if_needed(
        self,
        transaction: Transaction,
        sender: Union[IAccount, None],
        guardian: Union[IAccount, None],
        relayer: Union[IAccount, None],
    ):
        if (
            isinstance(sender, LedgerAccount)
            or isinstance(guardian, LedgerAccount)
            or isinstance(relayer, LedgerAccount)
        ):
            transaction_computer = TransactionComputer()
            transaction_computer.apply_options_for_hash_signing(transaction)

    def _sign_guarded_transaction_if_guardian(
        self,
        transaction: Transaction,
        guardian: Union[IAccount, None],
        guardian_service_url: Union[str, None],
        guardian_2fa_code: Union[str, None],
    ) -> Transaction:
        #  If the guardian account is provided, we sign locally. Otherwise, we reach for the trusted cosign service.
        if guardian:
            transaction.guardian_signature = guardian.sign_transaction(transaction)
        elif transaction.guardian and guardian_service_url and guardian_2fa_code:
            cosign_transaction(transaction, guardian_service_url, guardian_2fa_code)

        return transaction

    def _sign_relayed_transaction_if_relayer(self, transaction: Transaction, relayer: Union[IAccount, None]):
        if relayer and transaction.relayer:
            transaction.relayer_signature = relayer.sign_transaction(transaction)
