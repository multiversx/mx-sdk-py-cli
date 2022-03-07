
import logging
from argparse import ArgumentParser
from typing import cast

from erdpy.accounts import Account, Address
from erdpy.accounts_repository import AccountsRepository
from erdpy.proxy import ElrondProxy
from erdpy.proxy.core import ElrondProxy
from erdpy.transactions import BunchOfTransactions, Transaction


def main():
    """
    cd elrond-sdk-erdpy
    export PYTHONPATH=.
    python3 ./examples/airdrop.py \
        --proxy=https://testnet-gateway.elrond.com \
        --accounts=./erdpy/testnet/wallets/users \
        --sender=erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th\
        --value=1000000000000000000
    """

    logging.basicConfig(level=logging.ERROR)

    parser = ArgumentParser()
    parser.add_argument("--proxy", required=True)
    parser.add_argument("--accounts", required=True)
    parser.add_argument("--sender", help="sender address", required=True)
    parser.add_argument("--value", type=int, help="value, as a number (atoms of EGLD)")
    args = parser.parse_args()

    proxy = ElrondProxy(args.proxy)
    network = proxy.get_network_config()
    accounts = AccountsRepository.create_from_folder(args.accounts)
    sender = cast(Account, accounts.get_account(Address(args.sender)))
    sender.sync_nonce(proxy)
    receivers = [account for account in accounts.get_all() if account.address.bech32() != sender.address.bech32()]

    print("Sender", sender.address, "nonce", sender.nonce)

    transactions: BunchOfTransactions = BunchOfTransactions()

    for account in receivers:
        transaction = Transaction()
        transaction.nonce = sender.nonce
        transaction.sender = sender.address.bech32()
        transaction.receiver = account.address.bech32()
        transaction.value = str(args.value)
        transaction.gasPrice = network.min_gas_price
        transaction.gasLimit = 50000
        transaction.chainID = network.chain_id
        transaction.version = network.min_tx_version
        transaction.sign(sender)
        sender.nonce += 1

        transactions.add_prepared(transaction)

    num, hashes = transactions.send(proxy)
    print(f"Sent {num} transactions:")
    print(hashes)


if __name__ == "__main__":
    main()
