import logging
from argparse import ArgumentParser

from erdpy import utils
from erdpy.accounts import Account, Address
from erdpy.cli_output import CLIOutputBuilder
from erdpy.cli_password import load_password
from erdpy.transactions import Transaction
from erdpy_network.proxy_network_provider import ProxyNetworkProvider
from erdpy.validators.core import VALIDATORS_SMART_CONTRACT_ADDRESS, prepare_transaction_data_for_stake

logger = logging.getLogger("examples")


def main():
    """
    cd elrond-sdk-erdpy
    export PYTHONPATH=.
    python3 ./examples/staking.py \
        --proxy=https://testnet-gateway.elrond.com \
        --keyfile=~/elrondsdk/testwallets/latest/users/alice.json \
        --passfile=~/elrondsdk/testwallets/latest/users/password.txt \
        --reward-address="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th" \
        --validators-file=./erdpy/tests/testdata/validators.json \
        --value=2500000000000000000000
    """
    logging.basicConfig(level=logging.DEBUG)

    parser = ArgumentParser()
    parser.add_argument("--proxy", required=True)
    parser.add_argument("--keyfile", help="wallet JSON keyfile", required=True)
    parser.add_argument("--passfile", help="wallet keyfile's password file")
    parser.add_argument("--reward-address", required=True, help="the reward address")
    parser.add_argument("--validators-file", required=True, help="validators JSON file (with links to validator PEM files)")
    parser.add_argument("--value", type=int, required=True, help="value, as a number (atoms of EGLD)")
    args = parser.parse_args()

    proxy = ProxyNetworkProvider(args.proxy)
    network = proxy.get_network_config()
    password = load_password(args)
    node_operator = Account(key_file=args.keyfile, password=password)
    node_operator.sync_nonce(proxy)
    reward_address = Address(args.reward_address)
    data, gas_limit = prepare_transaction_data_for_stake(node_operator.address, args.validators_file, reward_address)

    tx = Transaction()
    tx.nonce = node_operator.nonce
    tx.value = str(args.value)
    tx.receiver = VALIDATORS_SMART_CONTRACT_ADDRESS
    tx.sender = node_operator.address.bech32()
    tx.gasPrice = network.min_gas_price
    tx.gasLimit = gas_limit
    tx.data = data
    tx.chainID = network.chain_id
    tx.version = network.min_transaction_version
    tx.sign(node_operator)

    utils.dump_out_json(CLIOutputBuilder().set_emitted_transaction(tx).build())
    tx_hash = tx.send(proxy)
    print("Transaction hash", tx_hash)


if __name__ == "__main__":
    main()
