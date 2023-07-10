import logging
from pathlib import Path
from typing import Any, Optional, Protocol

from multiversx_sdk_core import Address, MessageV1
from multiversx_sdk_network_providers.accounts import AccountOnNetwork
from multiversx_sdk_wallet import UserSigner

from multiversx_sdk_cli.constants import DEFAULT_HRP
from multiversx_sdk_cli.interfaces import IAccount, IAddress, ITransaction
from multiversx_sdk_cli.ledger.config import compare_versions
from multiversx_sdk_cli.ledger.ledger_app_handler import \
    SIGN_USING_HASH_VERSION
from multiversx_sdk_cli.ledger.ledger_functions import (
    TX_HASH_SIGN_OPTIONS, TX_HASH_SIGN_VERSION, do_get_ledger_address,
    do_get_ledger_version, do_sign_message_with_ledger,
    do_sign_transaction_with_ledger)

logger = logging.getLogger("accounts")


class INetworkProvider(Protocol):
    def get_account(self, address: IAddress) -> AccountOnNetwork:
        ...


class EmptyAddress(IAddress):
    def hex(self) -> str:
        return ""

    def bech32(self) -> str:
        return ""


class AccountBase(IAccount):
    def __init__(self, address: Any = EmptyAddress()) -> None:
        self.address = address
        self.nonce: int = 0

    def sync_nonce(self, proxy: INetworkProvider):
        logger.debug("AccountBase.sync_nonce()")
        self.nonce = proxy.get_account(self.address).nonce
        logger.debug(f"AccountBase.sync_nonce() done: {self.nonce}")

    def sign_transaction(self, transaction: ITransaction) -> str:
        raise NotImplementedError

    def sign_message(self, data: bytes) -> str:
        raise NotImplementedError


class Account(AccountBase):
    def __init__(self,
                 address: Any = None,
                 pem_file: Optional[str] = None,
                 pem_index: int = 0,
                 key_file: str = "",
                 password: str = "") -> None:
        super().__init__(address)

        if pem_file:
            pem_path = Path(pem_file).expanduser().resolve()
            self.signer = UserSigner.from_pem_file(pem_path, pem_index)
            self.address = Address(self.signer.get_pubkey().buffer, DEFAULT_HRP)
        elif key_file and password:
            key_file_path = Path(key_file).expanduser().resolve()
            self.signer = UserSigner.from_wallet(key_file_path, password)
            self.address = Address(self.signer.get_pubkey().buffer, DEFAULT_HRP)

    def sign_transaction(self, transaction: ITransaction) -> str:
        assert self.signer is not None
        return self.signer.sign(transaction).hex()

    def sign_message(self, data: bytes) -> str:
        assert self.signer is not None
        message = MessageV1(data)
        signature = self.signer.sign(message)

        logger.debug(f"Account.sign_message(): raw_data_to_sign = {data.hex()}, message_data_to_sign = {message.serialize_for_signing().hex()}, signature = {signature.hex()}")
        return signature.hex()


class LedgerAccount(Account):
    def __init__(self, account_index: int = 0, address_index: int = 0) -> None:
        super().__init__()
        self.account_index = account_index
        self.address_index = address_index
        self.address = Address.from_bech32(do_get_ledger_address(account_index=account_index, address_index=address_index))

    def sign_transaction(self, transaction: ITransaction) -> str:
        ledger_version = do_get_ledger_version()
        should_use_hash_signing = compare_versions(ledger_version, SIGN_USING_HASH_VERSION) >= 0
        if should_use_hash_signing:
            transaction.set_version(TX_HASH_SIGN_VERSION)
            transaction.set_options(TX_HASH_SIGN_OPTIONS)

        signature = do_sign_transaction_with_ledger(
            transaction.serialize_for_signing(),
            account_index=self.account_index,
            address_index=self.address_index,
            sign_using_hash=should_use_hash_signing
        )

        assert isinstance(signature, str)
        return signature

    def sign_message(self, data: bytes) -> str:
        message_length = len(data).to_bytes(4, byteorder="big")
        message_data_to_sign: bytes = message_length + data
        logger.debug(f"LedgerAccount.sign_message(): raw_data_to_sign = {data.hex()}, message_data_to_sign = {message_data_to_sign.hex()}")

        signature = do_sign_message_with_ledger(
            message_data_to_sign,
            account_index=self.account_index,
            address_index=self.address_index
        )

        assert isinstance(signature, str)

        logger.debug(f"LedgerAccount.sign_message(): signature = {signature}")
        return signature
