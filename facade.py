import logging

from erdpy import wallet
from erdpy.accounts import Account, Address
from erdpy.blockatlas import BlockAtlas
from erdpy.contracts import CodeMetadata, SmartContract
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

    # TODO: apply guards

    project = load_project(project_directory)
    bytecode = project.get_bytecode()
    metadata = CodeMetadata(metadata_upgradeable)
    contract = SmartContract(bytecode=bytecode, metadata=metadata)
    environment = TestnetEnvironment(proxy_url)
    owner = Account(pem_file=pem_file)

    def flow():
        tx_hash, address = environment.deploy_contract(contract, owner, arguments, gas_price, gas_limit, value)
        logger.info("Tx hash: %s", tx_hash)
        logger.info("Contract address: %s", address)

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

    contract = SmartContract(contract_address)
    environment = TestnetEnvironment(proxy_url)
    caller = Account(pem_file=pem_file)

    def flow():
        tx_hash = environment.execute_contract(contract, caller, function, arguments, gas_price, gas_limit, value)
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

    project = load_project(project_directory)
    bytecode = project.get_bytecode()
    metadata = CodeMetadata(metadata_upgradeable)
    contract = SmartContract(contract_address, bytecode=bytecode, metadata=metadata)
    environment = TestnetEnvironment(proxy_url)
    caller = Account(pem_file=pem_file)

    def flow():
        tx_hash = environment.upgrade_contract(contract, caller, arguments, gas_price, gas_limit, value)
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
    shard_id = args.shard_id
    proxy = ElrondProxy(proxy_url)
    nonce = proxy.get_last_block_nonce(shard_id)
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


def get_meta_nonce(args):
    proxy = ElrondProxy(args.proxy)
    nonce = proxy.get_meta_nonce()
    print(nonce)
    return nonce


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


def send_prepared_transaction(args):
    proxy = ElrondProxy(args.proxy)
    prepared = PreparedTransaction.from_file(args.tx)
    tx_hash = prepared.send(proxy)
    print(tx_hash)
    return tx_hash


def prepare_and_send_transaction(args):
    proxy = ElrondProxy(args.proxy)

    # Need to sync nonce
    owner = Account(pem_file=args.pem)
    owner.sync_nonce(proxy)
    args.nonce = owner.nonce

    prepared = do_prepare_transaction(args)
    tx_hash = prepared.send(proxy)
    print(tx_hash)
    return tx_hash


def prepare_and_send_stake_transaction(args):
    args = validators.parse_args_for_stake(args)
    return prepare_and_send_transaction(args)


def prepare_and_send_un_stake_transaction(args):
    args = validators.parse_args_for_un_stake(args)
    return prepare_and_send_transaction(args)


def prepare_and_send_un_jail_transaction(args):
    args = validators.parse_args_for_un_jail(args)
    return prepare_and_send_transaction(args)


def prepare_and_send_un_bond_transaction(args):
    args = validators.parse_args_for_un_bond(args)
    return prepare_and_send_transaction(args)


def prepare_and_send_change_reward_address_transaction(args):
    args = validators.parse_args_for_changing_reward_address(args)
    return prepare_and_send_transaction(args)


def prepare_and_send_claim_transaction(args):
    args = validators.parse_args_for_claim(args)
    return prepare_and_send_transaction(args)


def generate_pem(args):
    pem_file = args.pem

    seed, pubkey = wallet.generate_pair()
    address = Address(pubkey)
    pem.write(pem_file, seed, pubkey, name=address.bech32())
    logger.info(f"Created PEM file [{pem_file}].")


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
