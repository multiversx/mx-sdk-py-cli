from typing import Union

from multiversx_sdk import LedgerAccount, Transaction, TransactionComputer

from multiversx_sdk_cli.cosign_transaction import cosign_transaction
from multiversx_sdk_cli.interfaces import IAccount


def set_options_for_guarded_transaction_if_needed(transaction: Transaction):
    if transaction.guardian:
        transaction_computer = TransactionComputer()
        transaction_computer.apply_guardian(transaction, transaction.guardian)


def set_options_for_hash_signing_if_needed(
    transaction: Transaction,
    sender: IAccount,
    guardian: Union[IAccount, None],
    relayer: Union[IAccount, None],
):
    if isinstance(sender, LedgerAccount) or isinstance(guardian, LedgerAccount) or isinstance(relayer, LedgerAccount):
        transaction_computer = TransactionComputer()
        transaction_computer.apply_options_for_hash_signing(transaction)


def sign_guarded_transaction_if_guardian(
    transaction: Transaction,
    guardian: Union[IAccount, None],
    guardian_service_url: str,
    guardian_2fa_code: str,
) -> Transaction:
    if guardian:
        transaction.guardian_signature = guardian.sign_transaction(transaction)
    elif transaction.guardian and guardian_service_url and guardian_2fa_code:
        cosign_transaction(transaction, guardian_service_url, guardian_2fa_code)

    return transaction


def sign_relayed_transaction_if_relayer(transaction: Transaction, relayer: Union[IAccount, None]):
    if relayer and transaction.relayer:
        transaction.relayer_signature = relayer.sign_transaction(transaction)
