import logging
from typing import Any

from erdpy import errors, wallet
from erdpy.accounts import Account, Address
from erdpy.dispatcher.transactions.queue import TransactionQueue
from erdpy.proxy import ElrondProxy, TransactionCostEstimator
from erdpy.transactions import do_prepare_transaction
from erdpy.validators import validators
from erdpy.wallet import pem

logger = logging.getLogger("facade")


def get_transaction_cost(args: Any, tx_type: Any) -> Any:
    logger.debug("call_get_transaction_cost")

    cost_estimator = TransactionCostEstimator(args.proxy)
    result = cost_estimator.estimate_tx_cost(args, tx_type)
    print("Note: gas estimator is deprecated, will be updated on a future release.")
    print(result)
    return result


def prepare_nonce_in_args(args: Any):
    if args.recall_nonce:
        if args.pem:
            account = Account(pem_file=args.pem, pem_index=args.pem_index)
        elif args.keyfile and args.passfile:
            account = Account(key_file=args.keyfile, pass_file=args.passfile)
        else:
            raise errors.NoWalletProvided()

        account.sync_nonce(ElrondProxy(args.proxy))
        args.nonce = account.nonce


def prepare_and_send_stake_transaction(args: Any):
    prepare_nonce_in_args(args)
    args = validators.parse_args_for_stake(args)
    tx = do_prepare_transaction(args)

    try:
        tx.send(ElrondProxy(args.proxy))
    finally:
        tx.dump_to(args.outfile)


def prepare_and_send_unstake_transaction(args: Any):
    prepare_nonce_in_args(args)
    args = validators.parse_args_for_un_stake(args)
    tx = do_prepare_transaction(args)

    try:
        tx.send(ElrondProxy(args.proxy))
    finally:
        tx.dump_to(args.outfile)


def prepare_and_send_unjail_transaction(args: Any):
    prepare_nonce_in_args(args)
    args = validators.parse_args_for_un_jail(args)
    tx = do_prepare_transaction(args)

    try:
        tx.send(ElrondProxy(args.proxy))
    finally:
        tx.dump_to(args.outfile)


def prepare_and_send_unbond_transaction(args: Any):
    prepare_nonce_in_args(args)
    args = validators.parse_args_for_un_bond(args)
    tx = do_prepare_transaction(args)

    try:
        tx.send(ElrondProxy(args.proxy))
    finally:
        tx.dump_to(args.outfile)


def prepare_and_send_change_reward_address_transaction(args: Any):
    prepare_nonce_in_args(args)
    args = validators.parse_args_for_changing_reward_address(args)
    tx = do_prepare_transaction(args)

    try:
        tx.send(ElrondProxy(args.proxy))
    finally:
        tx.dump_to(args.outfile)


def prepare_and_send_claim_transaction(args: Any):
    prepare_nonce_in_args(args)
    args = validators.parse_args_for_claim(args)
    tx = do_prepare_transaction(args)

    try:
        tx.send(ElrondProxy(args.proxy))
    finally:
        tx.dump_to(args.outfile)


def enqueue_transaction(args: Any):
    queue = TransactionQueue()
    queue.enqueue_transaction(args)


def dispatch_transactions(args: Any):
    queue = TransactionQueue()
    queue.dispatch_transactions(args)


def dispatch_transactions_continuously(args: Any):
    queue = TransactionQueue()
    queue.dispatch_transactions_continuously(args)


def clean_transactions_queue():
    queue = TransactionQueue()
    queue.clean_transactions_queue()


def generate_pem(args: Any):
    pem_file = args.pem
    mnemonic = args.mnemonic

    seed, pubkey = wallet.generate_pair()
    if mnemonic:
        mnemonic = input("Enter mnemonic:\n")
        seed, pubkey = wallet.derive_keys(mnemonic)

    address = Address(pubkey)
    pem.write(pem_file, seed, pubkey, name=address.bech32())
    logger.info(f"Created PEM file [{pem_file}] for [{address.bech32()}]")


def do_bech32(args: Any):
    encode = args.encode
    value = args.value
    address = Address(value)

    result = address.bech32() if encode else address.hex()
    print(result)
    return result
