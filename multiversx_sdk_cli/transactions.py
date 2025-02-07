import json
import logging
import time
from pathlib import Path
from typing import Any, List, Protocol, TextIO, Union

from multiversx_sdk import (
    Account,
    Address,
    LedgerAccount,
    Token,
    TokenComputer,
    TokenTransfer,
    Transaction,
    TransactionComputer,
    TransactionOnNetwork,
    TransactionsFactoryConfig,
    TransferTransactionsFactory,
)

from multiversx_sdk_cli import config, errors
from multiversx_sdk_cli.cli_password import load_guardian_password, load_password
from multiversx_sdk_cli.cosign_transaction import cosign_transaction
from multiversx_sdk_cli.errors import IncorrectWalletError, NoWalletProvided
from multiversx_sdk_cli.interfaces import IAccount

logger = logging.getLogger("transactions")


# fmt: off
class INetworkProvider(Protocol):
    def send_transaction(self, transaction: Transaction) -> bytes:
        ...

    def get_transaction(self, transaction_hash: Union[bytes, str]) -> TransactionOnNetwork:
        ...
# fmt: on


def do_prepare_transaction(args: Any) -> Transaction:
    account = load_sender_account_from_args(args)

    native_amount = int(args.value)
    transfers = getattr(args, "token_transfers", [])
    transfers = prepare_token_transfers(transfers) if transfers else None

    config = TransactionsFactoryConfig(args.chain)
    factory = TransferTransactionsFactory(config)
    receiver = Address.new_from_bech32(args.receiver)

    if native_amount or transfers:
        tx = factory.create_transaction_for_transfer(
            sender=account.address,
            receiver=receiver,
            native_amount=native_amount,
            token_transfers=transfers,
            data=str(args.data).encode(),
        )
    else:
        # this is for transactions with no token transfers(egld/esdt); useful for setting the data field
        tx = Transaction(
            sender=account.address,
            receiver=receiver,
            data=str(args.data).encode(),
            gas_limit=int(args.gas_limit),
            chain_id=args.chain,
        )

    tx.gas_limit = int(args.gas_limit)
    tx.sender_username = getattr(args, "sender_username", None) or ""
    tx.receiver_username = getattr(args, "receiver_username", None) or ""
    tx.gas_price = int(args.gas_price)
    tx.nonce = int(args.nonce)
    tx.value = int(args.value)
    tx.version = int(args.version)
    tx.options = int(args.options)

    tx_computer = TransactionComputer()
    if isinstance(account, LedgerAccount):
        tx_computer.apply_options_for_hash_signing(tx)

    if args.guardian:
        tx.guardian = Address.new_from_bech32(args.guardian)

    if args.relayer:
        tx.relayer = Address.new_from_bech32(args.relayer)

        try:
            relayer_account = load_relayer_account_from_args(args)
            if relayer_account.address != tx.relayer:
                raise IncorrectWalletError("")

            if isinstance(relayer_account, LedgerAccount):
                tx_computer.apply_options_for_hash_signing(tx)

            tx.relayer_signature = relayer_account.sign_transaction(tx)
        except NoWalletProvided:
            logger.warning("Relayer wallet not provided. Transaction will not be signed by relayer.")
        except IncorrectWalletError:
            raise IncorrectWalletError("Relayer wallet does not match the relayer's address set in the transaction.")

    try:
        guardian_account = get_guardian_account_from_args(args)
        if isinstance(guardian_account, LedgerAccount):
            tx_computer.apply_options_for_hash_signing(tx)

    except NoWalletProvided:
        guardian_account = None

    tx.signature = account.sign_transaction(tx)
    tx = sign_tx_by_guardian(args, tx, guardian_account)

    return tx


def load_sender_account_from_args(args: Any) -> IAccount:
    hrp = config.get_address_hrp()

    if args.pem:
        return Account.new_from_pem(file_path=Path(args.pem), index=args.pem_index, hrp=hrp)
    elif args.keyfile:
        password = load_password(args)
        account = Account.new_from_keystore(
            file_path=Path(args.keyfile),
            password=password,
            address_index=args.address_index,
            hrp=hrp,
        )
    elif args.ledger:
        account = LedgerAccount(address_index=args.ledger_address_index)
    else:
        raise errors.NoWalletProvided()

    return account


def load_relayer_account_from_args(args: Any) -> IAccount:
    hrp = config.get_address_hrp()

    if args.relayer_ledger:
        account = LedgerAccount(address_index=args.relayer_ledger_address_index)
    if args.relayer_pem:
        account = Account.new_from_pem(file_path=Path(args.relayer_pem), index=args.relayer_pem_index, hrp=hrp)
    elif args.relayer_keyfile:
        password = load_password(args)
        account = Account.new_from_keystore(
            file_path=Path(args.relayer_keyfile),
            password=password,
            address_index=args.relayer_address_index,
            hrp=hrp,
        )
    else:
        raise errors.NoWalletProvided()

    return account


def prepare_token_transfers(transfers: List[Any]) -> List[TokenTransfer]:
    token_computer = TokenComputer()
    token_transfers: List[TokenTransfer] = []

    for i in range(0, len(transfers) - 1, 2):
        identifier = transfers[i]
        amount = int(transfers[i + 1])
        nonce = token_computer.extract_nonce_from_extended_identifier(identifier)

        token = Token(identifier, nonce)
        transfer = TokenTransfer(token, amount)
        token_transfers.append(transfer)

    return token_transfers


def sign_tx_by_guardian(args: Any, tx: Transaction, guardian_account: Union[IAccount, None]) -> Transaction:
    if guardian_account:
        tx.guardian_signature = guardian_account.sign_transaction(tx)
    elif args.guardian:
        tx = cosign_transaction(tx, args.guardian_service_url, args.guardian_2fa_code)  # type: ignore

    return tx


# TODO: this is duplicated code; a proper refactoring will come later
def get_guardian_account_from_args(args: Any) -> IAccount:
    hrp = config.get_address_hrp()

    if args.guardian_pem:
        account = Account.new_from_pem(file_path=Path(args.guardian_pem), index=args.guardian_pem_index, hrp=hrp)
    elif args.guardian_keyfile:
        password = load_guardian_password(args)
        account = Account.new_from_keystore(
            file_path=Path(args.guardian_keyfile),
            password=password,
            address_index=args.guardian_address_index,
            hrp=hrp,
        )
    elif args.guardian_ledger:
        account = LedgerAccount(address_index=args.relayer_ledger_address_index)
    else:
        raise errors.NoWalletProvided()

    return account


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
