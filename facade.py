import logging
from typing import Any

from erdpy import errors, utils, wallet
from erdpy.accounts import Account, Address
from erdpy.block import block
from erdpy.blockatlas import BlockAtlas
from erdpy.dispatcher.transactions.queue import TransactionQueue
from erdpy.proxy import ElrondProxy, TransactionCostEstimator
from erdpy.transactions import do_prepare_transaction
from erdpy.validators import validators
from erdpy.wallet import pem

logger = logging.getLogger("facade")


def get_account_nonce(args: Any) -> Any:
    proxy_url = args.proxy
    address = args.address

    proxy = ElrondProxy(proxy_url)
    nonce = proxy.get_account_nonce(Address(address))
    print(nonce)
    return nonce


def get_account_balance(args: Any) -> Any:
    proxy_url = args.proxy
    address = args.address

    proxy = ElrondProxy(proxy_url)
    balance = proxy.get_account_balance(Address(address))
    print(balance)
    return balance


def get_account(args: Any) -> Any:
    proxy_url = args.proxy
    address = args.address

    proxy = ElrondProxy(proxy_url)
    account = proxy.get_account(Address(address))
    print(account)
    return account


def get_account_transactions(args: Any) -> Any:
    proxy_url = args.proxy
    address = args.address

    proxy = ElrondProxy(proxy_url)
    response = proxy.get_account_transactions(Address(address))
    utils.dump_out_json(response, args.outfile)
    return response


def get_num_shards(args):
    proxy_url = args.proxy
    proxy = ElrondProxy(proxy_url)
    num_shards = proxy.get_num_shards()
    print(num_shards)
    return num_shards


def get_last_block_nonce(args):
    proxy_url = args.proxy
    shard = args.shard
    proxy = ElrondProxy(proxy_url)
    nonce = proxy.get_last_block_nonce(shard)
    print(nonce)
    return nonce


def get_gas_price(args: Any) -> Any:
    proxy_url = args.proxy
    proxy = ElrondProxy(proxy_url)
    price = proxy.get_gas_price()
    print(price)
    return price


def get_chain_id(args):
    proxy_url = args.proxy
    proxy = ElrondProxy(proxy_url)
    chain_id = proxy.get_chain_id()
    print(chain_id)
    return chain_id


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


def blockatlas_get_current_block_number(args: Any) -> Any:
    client = BlockAtlas(args.url, args.coin)
    number = client.get_current_block_number()
    print(number)
    return number


def blockatlas_get_block_by_number(args: Any) -> Any:
    client = BlockAtlas(args.url, args.coin)
    block = client.get_block_by_number(args.number)
    print(block)
    return block


def blockatlas_get_txs_by_address(args: Any) -> Any:
    client = BlockAtlas(args.url, args.coin)
    transactions = client.get_txs_by_address(args.address)
    utils.dump_out_json(transactions, args.outfile)
    return transactions


def get_block(args: Any) -> Any:
    block.get_block(args)
