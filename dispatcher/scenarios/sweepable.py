# This is an scenario example used to test a particular scenario within our system tests

import logging
import sys
from argparse import ArgumentParser

from erdpy import errors
from erdpy.accounts import AccountsRepository
from erdpy.proxy import ElrondProxy
from erdpy.transactions import BunchOfTransactions

logger = logging.getLogger("dipatcher.scenarios")

GAS_PRICE = 100000000000000
GAS_LIMIT = 50000


def main():
    parser = ArgumentParser()
    parser.add_argument("--proxy", required=True)
    parser.add_argument("--senders-folder", required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    proxy = ElrondProxy(args.proxy)
    bunch = BunchOfTransactions()
    senders_repository = AccountsRepository(args.senders_folder)

    for sender in senders_repository.get_all():
        sender.sync_nonce()

        # Send bad transactions to self
        nonce = sender.nonce + 42
        value = 42
        bunch.add(sender, sender.address.bech32(), nonce, value, "", GAS_PRICE, GAS_LIMIT)
        nonce += 1

    bunch.send(proxy)


if __name__ == "__main__":
    try:
        main()
    except errors.KnownError as err:
        logger.fatal(err)
        sys.exit(1)
