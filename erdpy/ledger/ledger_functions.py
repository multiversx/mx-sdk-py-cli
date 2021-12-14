import logging
from erdpy.ledger.ledger_app_handler import ElrondLedgerApp

TX_HASH_SIGN_VERSION = 2
TX_HASH_SIGN_OPTIONS = 1

logger = logging.getLogger("ledger")


def do_sign_transaction_with_ledger(
        tx_payload: bytes,
        account_index: int,
        address_index: int,
        sign_using_hash: bool
) -> str:
    ledger_handler = ElrondLedgerApp()
    ledger_handler.set_address(account_index=account_index, address_index=address_index)

    logger.info("Ledger: please confirm the transaction on the device")
    signature = ledger_handler.sign_transaction(tx_payload, sign_using_hash)
    ledger_handler.close()

    return signature


def do_get_ledger_address(account_index: int, address_index: int) -> str:
    ledger_handler = ElrondLedgerApp()
    ledger_address = ledger_handler.get_address(account_index=account_index, address_index=address_index)
    ledger_handler.close()

    return ledger_address


def do_get_ledger_version() -> str:
    ledger_handler = ElrondLedgerApp()
    ledger_version = ledger_handler.get_version()
    ledger_handler.close()

    return ledger_version
