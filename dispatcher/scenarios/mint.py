import logging
import sys
from argparse import ArgumentParser

from erdpy import errors
from erdpy.accounts import Account, AccountsRepository
from erdpy.proxy import ElrondProxy
from erdpy.transactions import BunchOfTransactions

logger = logging.getLogger("dipatcher.scenarios")

GAS_PRICE = 100000000000000
GAS_LIMIT = 50000
MINTED_VALUE = 10


def main():
    parser = ArgumentParser()
    parser.add_argument("--proxy", required=True)
    parser.add_argument("--minter", required=True)
    parser.add_argument("--minted-value", required=False, type=int, default=MINTED_VALUE)
    parser.add_argument("--minted-folder", required=True)
    parser.add_argument("--minted-count", required=False, type=int)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    proxy = ElrondProxy(args.proxy)
    bunch = BunchOfTransactions()
    minter = Account(pem_file=args.minter)
    minted_repository = AccountsRepository(args.minted_folder)

    if args.minted_count:
        minted_repository.generate_accounts(args.minted_count)

    minter.sync_nonce(proxy)
    nonce = minter.nonce
    value = args.minted_value
    for minted in minted_repository.get_all():
        bunch.add(minter, minted.address.bech32(), nonce, value, "", GAS_PRICE, GAS_LIMIT)
        nonce += 1

    bunch.send(proxy)


if __name__ == "__main__":
    try:
        main()
    except errors.KnownError as err:
        logger.fatal(err)
        sys.exit(1)
