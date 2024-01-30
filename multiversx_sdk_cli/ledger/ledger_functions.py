import logging

from multiversx_sdk_cli import config
from multiversx_sdk_cli.ledger.ledger_app_handler import LedgerApp

TX_HASH_SIGN_VERSION = 2
TX_HASH_SIGN_OPTIONS = 1

logger = logging.getLogger("ledger")


class LedgerFacade:
    def __init__(self):
        self.debug = config.is_ledger_debug_enabled()

    def do_sign_transaction_with_ledger(
            self,
            tx_payload: bytes,
            account_index: int,
            address_index: int,
            sign_using_hash: bool
    ) -> str:
        app = LedgerApp(debug=self.debug)
        app.set_address(account_index=account_index, address_index=address_index)

        logger.info("Ledger: please confirm the transaction on the device")
        signature = app.sign_transaction(tx_payload, sign_using_hash)
        app.close()

        return signature

    def do_sign_message_with_ledger(
            self,
            message_payload: bytes,
            account_index: int,
            address_index: int
    ) -> str:
        app = LedgerApp(debug=self.debug)
        app.set_address(account_index=account_index, address_index=address_index)

        logger.info("Ledger: please confirm the message on the device")
        signature = app.sign_message(message_payload)
        app.close()

        return signature

    def do_get_ledger_address(self, account_index: int, address_index: int) -> str:
        app = LedgerApp(debug=self.debug)
        address = app.get_address(account_index=account_index, address_index=address_index)
        app.close()

        return address

    def do_get_ledger_version(self) -> str:
        app = LedgerApp(debug=self.debug)
        version = app.get_version()
        app.close()

        return version
