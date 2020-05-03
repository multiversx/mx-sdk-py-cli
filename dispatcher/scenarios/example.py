import logging
import sys
from argparse import ArgumentParser

from erdpy import errors
from erdpy.accounts import AccountsRepository
from erdpy.proxy import ElrondProxy
from erdpy.transactions import BunchOfTransactions

logger = logging.getLogger("dipatcher.scenario")


def main():
    parser = ArgumentParser()
    parser.add_argument("--proxy", required=True)
    parser.add_argument("--pem-folder", required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    proxy = ElrondProxy(args.proxy)
    accounts_repository = AccountsRepository(args.pem_folder)
    bob = accounts_repository.get_account("bob")
    bob.sync_nonce(proxy)

    bunch = BunchOfTransactions()
    bunch.add(bob, "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz", bob.nonce, 10, "", 100000000000000, 50000)
    bunch.add(bob, "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz", bob.nonce + 1, 10, "", 100000000000000, 50000)
    bunch.send(proxy)


if __name__ == "__main__":
    try:
        main()
    except errors.KnownError as err:
        logger.fatal(err)
        sys.exit(1)
