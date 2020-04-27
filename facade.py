import logging

from erdpy import guards
from erdpy.accounts import Account, Address
from erdpy.contracts import SmartContract, CodeMetadata
from erdpy.environments import TestnetEnvironment
from erdpy.projects import load_project
from erdpy.proxy import ElrondProxy, TransactionCostEstimator
from erdpy.transactions import PreparedTransaction, do_prepare_transaction

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


def get_account_nonce(proxy_url, address):
    logger.debug("call_get_account_nonce")

    proxy = ElrondProxy(proxy_url)
    nonce = proxy.get_account_nonce(Address(address))
    print(nonce)
    return nonce


def get_account_balance(proxy_url, address):
    logger.debug("call_get_account_balance")

    proxy = ElrondProxy(proxy_url)
    balance = proxy.get_account_balance(Address(address))
    print(balance)
    return balance


def get_account(proxy_url, address):
    logger.debug("call_get_account")

    proxy = ElrondProxy(proxy_url)
    account = proxy.get_account(Address(address))
    print(account)
    return account


def get_num_shards(proxy_url):
    logger.debug("call_get_number_of_shards")

    proxy = ElrondProxy(proxy_url)
    num_shards = proxy.get_num_shards()
    print(num_shards)
    return num_shards


def get_last_block_nonce(proxy_url, shard_id):
    logger.debug("call_get_last_block_nonce")

    proxy = ElrondProxy(proxy_url)
    nonce = proxy.get_last_block_nonce(shard_id)
    print(nonce)
    return nonce


def get_gas_price(proxy_url):
    logger.debug("call_get_gas_price")

    proxy = ElrondProxy(proxy_url)
    price = proxy.get_gas_price()
    print(price)
    return price


def get_chain_id(proxy_url):
    logger.debug("call_get_chain_id")

    proxy = ElrondProxy(proxy_url)
    chain_id = proxy.get_chain_id()
    print(chain_id)
    return chain_id


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


def do_bech32(args):
    encode = args.encode
    value = args.value
    address = Address(value)

    result = address.bech32() if encode else address.hex()
    print(result)
    return result
