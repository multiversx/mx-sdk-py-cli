import logging

from erdpy import utils, wallet
from erdpy.accounts import Account, Address
from erdpy.blockatlas import BlockAtlas
from erdpy.contracts import CodeMetadata, SmartContract
from erdpy.dispatcher.transactions.queue import TransactionQueue
from erdpy.environments import TestnetEnvironment
from erdpy.projects import load_project
from erdpy.proxy import ElrondProxy, TransactionCostEstimator
from erdpy.transactions import PreparedTransaction, do_prepare_transaction
from erdpy.validators import validators
from erdpy.wallet import pem

logger = logging.getLogger("facade")


def deploy_smart_contract(args):
    logger.debug("deploy_smart_contract")

    project_directory = args.project
    pem_file = args.pem
    proxy_url = args.proxy
    arguments = args.arguments
    gas_price = args.gas_price
    gas_limit = args.gas_limit
    value = args.value
    metadata_upgradeable = args.metadata_upgradeable
    chain = args.chain
    version = args.version

    # TODO: apply guards

    project = load_project(project_directory)
    bytecode = project.get_bytecode()
    metadata = CodeMetadata(metadata_upgradeable)
    contract = SmartContract(bytecode=bytecode, metadata=metadata)
    environment = TestnetEnvironment(proxy_url)
    owner = Account(pem_file=pem_file)

    def flow():
        tx_hash, address = environment.deploy_contract(contract, owner, arguments, gas_price, gas_limit, value, chain, version)
        logger.info("Tx hash: %s", tx_hash)
        logger.info("Contract address: %s", address)
        utils.dump_out_json({"tx": tx_hash, "contract": address.bech32()}, args.outfile)

    environment.run_flow(flow)


def call_smart_contract(args):
    logger.debug("call_smart_contract")

    contract_address = args.contract
    pem_file = args.pem
    proxy_url = args.proxy
    function = args.function
    arguments = args.arguments
    gas_price = args.gas_price
    gas_limit = args.gas_limit
    value = args.value
    chain = args.chain
    version = args.version

    contract = SmartContract(contract_address)
    environment = TestnetEnvironment(proxy_url)
    caller = Account(pem_file=pem_file)

    def flow():
        tx_hash = environment.execute_contract(contract, caller, function, arguments, gas_price, gas_limit, value, chain, version)
        logger.info("Tx hash: %s", tx_hash)

    environment.run_flow(flow)


def upgrade_smart_contract(args):
    logger.debug("upgrade_smart_contract")

    contract_address = args.contract
    project_directory = args.project
    pem_file = args.pem
    proxy_url = args.proxy
    arguments = args.arguments
    gas_price = args.gas_price
    gas_limit = args.gas_limit
    value = args.value
    metadata_upgradeable = args.metadata_upgradeable
    chain = args.chain
    version = args.version

    project = load_project(project_directory)
    bytecode = project.get_bytecode()
    metadata = CodeMetadata(metadata_upgradeable)
    contract = SmartContract(contract_address, bytecode=bytecode, metadata=metadata)
    environment = TestnetEnvironment(proxy_url)
    caller = Account(pem_file=pem_file)

    def flow():
        tx_hash = environment.upgrade_contract(contract, caller, arguments, gas_price, gas_limit, value, chain, version)
        logger.info("Tx hash: %s", tx_hash)

    environment.run_flow(flow)


def query_smart_contract(args):
    logger.debug("query_smart_contract")

    contract_address = args.contract
    proxy_url = args.proxy
    function = args.function
    arguments = args.arguments

    contract = SmartContract(contract_address)
    environment = TestnetEnvironment(proxy_url)

    def flow():
        result = environment.query_contract(contract, function, arguments)
        print(result)

    environment.run_flow(flow)


def get_account_nonce(args):
    proxy_url = args.proxy
    address = args.address

    proxy = ElrondProxy(proxy_url)
    nonce = proxy.get_account_nonce(Address(address))
    print(nonce)
    return nonce


def get_account_balance(args):
    proxy_url = args.proxy
    address = args.address

    proxy = ElrondProxy(proxy_url)
    balance = proxy.get_account_balance(Address(address))
    print(balance)
    return balance


def get_account(args):
    proxy_url = args.proxy
    address = args.address

    proxy = ElrondProxy(proxy_url)
    account = proxy.get_account(Address(address))
    print(account)
    return account


def get_account_transactions(args):
    proxy_url = args.proxy
    address = args.address

    proxy = ElrondProxy(proxy_url)
    account = proxy.get_account_transactions(Address(address))
    print(account)
    return account


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


def get_gas_price(args):
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


def get_meta_block(args):
    proxy = ElrondProxy(args.proxy)
    block = proxy.get_meta_block(args.nonce)
    print(block)
    return block


def get_transaction_cost(args):
    logger.debug("call_get_transaction_cost")

    cost_estimator = TransactionCostEstimator(args.proxy)
    result = cost_estimator.estimate_tx_cost(args)
    print(result)
    return result


# DEPRECATED
def send_prepared_transaction(args):
    proxy = ElrondProxy(args.proxy)
    prepared = PreparedTransaction.from_file(args.tx)
    tx_hash = prepared.send(proxy)
    print(tx_hash)
    return tx_hash


# DEPRECATED
def prepare_and_send_transaction(args):
    proxy = ElrondProxy(args.proxy)

    if args.recall_nonce:
        owner = Account(pem_file=args.pem)
        owner.sync_nonce(proxy)
        args.nonce = owner.nonce

    prepared = do_prepare_transaction(args)
    tx_hash = prepared.send(proxy)
    print(tx_hash)
    return tx_hash


def create_transaction(args):
    args = utils.as_object(args)

    proxy = ElrondProxy(args.proxy)

    if args.recall_nonce:
        owner = Account(pem_file=args.pem)
        owner.sync_nonce(proxy)
        args.nonce = owner.nonce

    if args.data_file:
        args.data = utils.read_file(args.data_file)

    output = utils.Object()
    prepared = do_prepare_transaction(args)
    output.tx = prepared.to_dictionary()

    try:
        if args.send:
            output.hash = prepared.send(proxy)
    finally:
        # Save output even if there's an error during the actual send
        args.outfile.writelines([output.to_json(), "\n"])


def send_transaction(args):
    args = utils.as_object(args)

    proxy = ElrondProxy(args.proxy)

    output = utils.Object()
    prepared = PreparedTransaction.from_file(args.infile)
    output.tx = prepared.to_dictionary()
    output.hash = prepared.send(proxy)
    args.outfile.writelines([output.to_json(), "\n"])


def prepare_and_send_stake_transaction(args):
    args = validators.parse_args_for_stake(args)
    return prepare_and_send_transaction(args)


def prepare_and_send_unstake_transaction(args):
    args = validators.parse_args_for_un_stake(args)
    return prepare_and_send_transaction(args)


def prepare_and_send_unjail_transaction(args):
    args = validators.parse_args_for_un_jail(args)
    return prepare_and_send_transaction(args)


def prepare_and_send_unbond_transaction(args):
    args = validators.parse_args_for_un_bond(args)
    return prepare_and_send_transaction(args)


def prepare_and_send_change_reward_address_transaction(args):
    args = validators.parse_args_for_changing_reward_address(args)
    return prepare_and_send_transaction(args)


def prepare_and_send_claim_transaction(args):
    args = validators.parse_args_for_claim(args)
    return prepare_and_send_transaction(args)


def enqueue_transaction(args):
    queue = TransactionQueue()
    queue.enqueue_transaction(args)


def dispatch_transactions(args):
    queue = TransactionQueue()
    queue.dispatch_transactions(args)


def dispatch_transactions_continuously(args):
    queue = TransactionQueue()
    queue.dispatch_transactions_continuously(args)


def clean_transactions_queue():
    queue = TransactionQueue()
    queue.clean_transactions_queue()


def generate_pem(args):
    pem_file = args.pem
    mnemonic = args.mnemonic

    seed, pubkey = wallet.generate_pair()
    if mnemonic:
        mnemonic = input("Enter mnemonic:\n")
        seed, pubkey = wallet.derive_keys(mnemonic)

    address = Address(pubkey)
    pem.write(pem_file, seed, pubkey, name=address.bech32())
    logger.info(f"Created PEM file [{pem_file}] for [{address.bech32()}]")


def do_bech32(args):
    encode = args.encode
    value = args.value
    address = Address(value)

    result = address.bech32() if encode else address.hex()
    print(result)
    return result


def blockatlas_get_current_block_number(args):
    client = BlockAtlas(args.url, args.coin)
    number = client.get_current_block_number()
    print(number)
    return number


def blockatlas_get_block_by_number(args):
    client = BlockAtlas(args.url, args.coin)
    block = client.get_block_by_number(args.number)
    print(block)
    return block


def blockatlas_get_txs_by_address(args):
    client = BlockAtlas(args.url, args.coin)
    transactions = client.get_txs_by_address(args.address)
    print(transactions)
    return transactions
