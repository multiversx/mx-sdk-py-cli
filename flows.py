import logging

from erdpy.accounts import Account
from erdpy.contracts import SmartContract
from erdpy.environments import TestnetEnvironment
from erdpy.projects import load_project
from erdpy.proxy import ElrondProxy, TransactionCostEstimator
from erdpy.transactions import PreparedTransaction

logger = logging.getLogger("examples")


def deploy_smart_contract(project_directory, pem_file, proxy_url, arguments, gas_price, gas_limit):
    logger.debug("deploy_smart_contract")

    project = load_project(project_directory)
    bytecode = project.get_bytecode()
    contract = SmartContract(bytecode=bytecode)
    environment = TestnetEnvironment(proxy_url)
    owner = Account(pem_file=pem_file)

    def flow():
        tx, address = environment.deploy_contract(contract, owner, arguments, gas_price, gas_limit)
        logger.info("Tx hash: %s", tx)
        logger.info("Contract address: %s", address)

    environment.run_flow(flow)


def call_smart_contract(contract_address, pem_file, proxy_url, function, arguments, gas_price, gas_limit):
    logger.debug("call_smart_contract")

    contract = SmartContract(contract_address)
    environment = TestnetEnvironment(proxy_url)
    caller = Account(pem_file=pem_file)

    def flow():
        environment.execute_contract(contract, caller, function, arguments, gas_price, gas_limit)

    environment.run_flow(flow)


def query_smart_contract(contract_address, proxy_url, function, arguments):
    logger.debug("query_smart_contract")

    contract = SmartContract(contract_address)
    environment = TestnetEnvironment(proxy_url)

    def flow():
        environment.query_contract(contract, function, arguments)

    environment.run_flow(flow)


def get_account_nonce(proxy_url, address):
    logger.debug("call_get_account_nonce")

    proxy = ElrondProxy(proxy_url)
    nonce = proxy.get_account_nonce(address)
    print(nonce)
    return nonce


def get_account_balance(proxy_url, address):
    logger.debug("call_get_account_balance")

    proxy = ElrondProxy(proxy_url)
    balance = proxy.get_account_balance(address)
    print(balance)
    return balance


def get_account(proxy_url, address):
    logger.debug("call_get_account")

    proxy = ElrondProxy(proxy_url)
    account = proxy.get_account(address)
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


def get_transaction_cost(arguments):
    logger.debug("call_get_transaction_cost")

    cost_estimator = TransactionCostEstimator(arguments.proxy)
    cost_estimator.estimate_tx_cost(arguments)


def send_prepared_transaction(args):
    proxy = ElrondProxy(args.proxy)
    prepared = PreparedTransaction.from_file(args.tx)
    prepared.send(proxy)
