from typing import Optional, Union

from multiversx_sdk import LedgerAccount, Transaction, TransactionComputer

from multiversx_sdk_cli.cosign_transaction import cosign_transaction
from multiversx_sdk_cli.errors import TransactionSigningError
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.interfaces import IAccount


class SigningWrapper:
    def __init__(self):
        pass

    def sign_transaction(
        self,
        transaction: Transaction,
        sender: Optional[IAccount] = None,
        guardian_and_relayer: GuardianRelayerData = GuardianRelayerData(),
    ):
        """Signs the transaction using the sender's account and, if required, additionally signs with the guardian's and relayer's accounts. Ensures the appropriate transaction options are set as needed."""
        self._set_options_for_guarded_transaction_if_needed(transaction)

        guardian = guardian_and_relayer.guardian
        relayer = guardian_and_relayer.relayer
        guardian_service_url = guardian_and_relayer.guardian_service_url
        guardian_2fa_code = guardian_and_relayer.guardian_2fa_code

        self._set_options_for_hash_signing_if_needed(transaction, sender, guardian, relayer)

        if sender:
            try:
                transaction.signature = sender.sign_transaction(transaction)
            except Exception as e:
                raise TransactionSigningError(f"Could not sign transaction: {str(e)}")

        self._sign_guarded_transaction_if_guardian(
            transaction,
            guardian,
            guardian_service_url,
            guardian_2fa_code,
        )
        self._sign_relayed_transaction_if_relayer(transaction, relayer)

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
        transaction_computer = TransactionComputer()

        if (
            isinstance(sender, LedgerAccount)
            or isinstance(guardian, LedgerAccount)
            or isinstance(relayer, LedgerAccount)
        ):
            transaction_computer.apply_options_for_hash_signing(transaction)
            return

        if sender and sender.use_hash_signing:
            transaction_computer.apply_options_for_hash_signing(transaction)
            return

        if guardian and guardian.use_hash_signing:
            transaction_computer.apply_options_for_hash_signing(transaction)
            return

        if relayer and relayer.use_hash_signing:
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
            try:
                transaction.guardian_signature = guardian.sign_transaction(transaction)
            except Exception as e:
                raise TransactionSigningError(f"Could not sign transaction: {str(e)}")
        elif transaction.guardian and guardian_service_url and guardian_2fa_code:
            cosign_transaction(transaction, guardian_service_url, guardian_2fa_code)

        return transaction

    def _sign_relayed_transaction_if_relayer(self, transaction: Transaction, relayer: Union[IAccount, None]):
        if relayer and transaction.relayer:
            try:
                transaction.relayer_signature = relayer.sign_transaction(transaction)
            except Exception as e:
                raise TransactionSigningError(f"Could not sign transaction: {str(e)}")
