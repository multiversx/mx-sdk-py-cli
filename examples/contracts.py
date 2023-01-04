import logging
from argparse import ArgumentParser
from pathlib import Path
from erdpy import utils

from erdpy.accounts import Account, Address
from erdpy.contracts import CodeMetadata, SmartContract
from erdpy_network_providers.proxy_network_provider import ProxyNetworkProvider

logger = logging.getLogger("examples")


if __name__ == '__main__':
    """
    cd elrond-sdk-erdpy
    export PYTHONPATH=.
    python3 ./examples/contracts.py \
        --proxy=https://testnet-gateway.elrond.com \
        --pem=~/elrondsdk/testwallets/latest/users/alice.pem

    Sample contracts to be used (at deploy & upgrade):
        ./examples/bytecode/counter.wasm (functions: increment, decrement, get)
        ./examples/bytecode/answer.wasm (functions: getUltimateAnswer)
    """

    parser = ArgumentParser()
    parser.add_argument("--proxy", required=True)
    parser.add_argument("--pem", required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    proxy = ProxyNetworkProvider(args.proxy)
    network = proxy.get_network_config()
    user = Account(pem_file=args.pem)

    def do_deploy():
        bytecode_path = Path(input("Path to WASM: ")).absolute()
        bytecode = utils.read_binary_file(bytecode_path).hex()
        code_metadata = CodeMetadata(upgradeable=True)
        contract = SmartContract(bytecode=bytecode, metadata=code_metadata)

        user.sync_nonce(proxy)

        tx = contract.deploy(
            owner=user,
            arguments=[],
            gas_price=network.min_gas_price,
            gas_limit=5000000,
            value=0,
            chain=network.chain_id,
            version=network.min_transaction_version
        )

        tx_on_network = tx.send_wait_result(proxy, 5000)

        logger.info(f"Deployment transaction: {tx_on_network.get_hash()}")
        logger.info(f"Contract address: {contract.address.bech32()}",)

    def do_query():
        contract_address = Address(input("Contract address: "))
        contract = SmartContract(address=contract_address)

        function = input("Name of function: ")
        answer = contract.query(proxy, function, [])
        logger.info(f"Answer: {answer}")

    def do_execute():
        contract_address = Address(input("Contract address: "))
        contract = SmartContract(address=contract_address)
        function = input("Name of function: ")

        user.sync_nonce(proxy)

        tx = contract.execute(
            caller=user,
            function=function,
            arguments=[],
            gas_price=network.min_gas_price,
            gas_limit=5000000,
            value=0,
            chain=network.chain_id,
            version=network.min_tx_version
        )

        tx_hash = tx.send(proxy)
        logger.info(f"Transaction: {tx_hash}")

    def do_upgrade():
        contract_address = Address(input("Contract address: "))
        bytecode_path = Path(input("Path to WASM: ")).absolute()
        bytecode = utils.read_binary_file(bytecode_path).hex()
        code_metadata = CodeMetadata(upgradeable=True)
        contract = SmartContract(address=contract_address, bytecode=bytecode, metadata=code_metadata)

        user.sync_nonce(proxy)

        tx = contract.upgrade(
            owner=user,
            arguments=[],
            gas_price=network.min_gas_price,
            gas_limit=5000000,
            value=0,
            chain=network.chain_id,
            version=network.min_tx_version
        )

        tx_on_network = tx.send_wait_result(proxy, 5000)

        logger.info(f"Upgrade transaction: {tx_on_network.get_hash()}")

    while True:
        print("Let's run a flow.")
        print("1. Deploy")
        print("2. Query")
        print("3. Call")
        print("4. Upgrade")

        try:
            choice = int(input("Choose:\n"))
        except Exception:
            break

        flows = [
            None,
            do_deploy,
            do_query,
            do_execute,
            do_upgrade
        ]

        flow = flows[choice]
        if flow:
            flow()
        else:
            print("Bad choice")
            break
