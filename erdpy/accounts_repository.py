import logging
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import List, Set, Union

from erdpy import utils
from erdpy.accounts import Account, Address
from erdpy.interfaces import IElrondProxy
from erdpy.wallet import pem

logger = logging.getLogger("accounts")


class AccountsRepository:
    def __init__(self, accounts: List[Account]):
        self.accounts = accounts

    @classmethod
    def create_from_folder(cls, folder: Path) -> 'AccountsRepository':
        """
        Creates an AccountsRepository using a folder containing *.pem files.
        """
        files = utils.list_files(folder, suffix=".pem")
        return cls.create_from_files(files)

    @classmethod
    def create_from_files(cls, files: List[Path]) -> 'AccountsRepository':
        """
        Creates an AccountsRepository using a list of *.pem files.
        """
        accounts_loaded: List[Account] = []

        for file in files:
            # Assume multi-account PEM files.
            key_pairs = pem.parse_all(file)

            for seed, pubkey in key_pairs:
                account = Account()
                account.secret_key = seed.hex()
                account.address = Address(pubkey)
                accounts_loaded.append(account)

        # Deduplicate accounts (by address)
        addresses: Set[str] = set()
        accounts_deduplicated: List[Account] = []

        for account in accounts_loaded:
            address = account.address.bech32()

            if address not in addresses:
                addresses.add(address)
                accounts_deduplicated.append(account)

        logger.info(f"loaded {len(accounts_deduplicated)} accounts from {len(files)} PEM files.")
        return AccountsRepository(accounts_deduplicated)

    def get_account(self, address: Address) -> Union[Account, None]:
        try:
            return next(account for account in self.accounts if account.address.bech32() == address.bech32())
        except StopIteration:
            return None

    def get_all(self) -> List[Account]:
        return self.accounts

    def __len__(self):
        return len(self.accounts)

    def sync_nonces(self, proxy: IElrondProxy, num_parallel: int = 10):
        logger.info("Sync nonces for", len(self.accounts), "accounts")

        def sync_nonce(account: Account):
            account.sync_nonce(proxy)

        ThreadPool(num_parallel).map(sync_nonce, self.accounts)

        logger.info("Done")
