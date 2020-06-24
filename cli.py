import logging
import os
import sys
from argparse import ArgumentParser

from erdpy import (cli_contracts, cli_install, config, errors,
                   facade, proxy, transactions)
from erdpy._version import __version__

logger = logging.getLogger("cli")


def main():
    try:
        _do_main()
    except errors.KnownError as err:
        logger.fatal(err)
        sys.exit(1)


def _do_main():
    parser = setup_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARN)

    if not hasattr(args, "func"):
        parser.print_help()
    else:
        args.func(args)


def setup_parser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    parser.add_argument('-v', '--version', action='version', version=f"erdpy {__version__}")
    parser.add_argument("--verbose", action="store_true", default=False)

    cli_install.setup_parser_install(subparsers)
    cli_contracts.setup_parser_contract(subparsers)

    tx_prepare_parser = subparsers.add_parser("tx-prepare")
    tx_prepare_parser.add_argument("--pem", required=True)
    tx_prepare_parser.add_argument("--nonce", type=int, required=True)
    tx_prepare_parser.add_argument("--value", default="0")
    tx_prepare_parser.add_argument("--receiver", required=True)
    tx_prepare_parser.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    tx_prepare_parser.add_argument("--gas-limit", required=True)
    tx_prepare_parser.add_argument("--data", default="")
    tx_prepare_parser.add_argument("--tag", default="untitled")
    tx_prepare_parser.add_argument("workspace", nargs='?', default=os.getcwd())
    tx_prepare_parser.set_defaults(func=tx_prepare)

    tx_send_parser = subparsers.add_parser("tx-send")
    tx_send_parser.add_argument("tx")
    tx_send_parser.add_argument("--proxy", required=True)
    tx_send_parser.set_defaults(func=tx_send)

    tx_prepare_and_send_parser = subparsers.add_parser("tx-prepare-and-send")
    tx_prepare_and_send_parser.add_argument("--pem", required=True)
    tx_prepare_and_send_parser.add_argument("--nonce", type=int, required=True)
    tx_prepare_and_send_parser.add_argument("--value", default="0")
    tx_prepare_and_send_parser.add_argument("--receiver", required=True)
    tx_prepare_and_send_parser.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    tx_prepare_and_send_parser.add_argument("--gas-limit", required=True)
    tx_prepare_and_send_parser.add_argument("--data", default="")
    tx_prepare_and_send_parser.add_argument("--proxy", required=True)
    tx_prepare_and_send_parser.set_defaults(func=tx_prepare_and_send)

    setup_parser_accounts(subparsers)
    setup_parser_validators(subparsers)
    setup_parser_wallet(subparsers)
    setup_parser_cost(subparsers)
    setup_parser_network(subparsers)
    setup_parser_blockatlas(subparsers)
    setup_parser_queue(subparsers)

    return parser


def setup_parser_accounts(subparsers):
    parser = subparsers.add_parser("account")
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("get")
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--address", required=True)
    sub.add_argument("--balance", required=False, nargs='?', const=True, default=False)
    sub.add_argument("--nonce", required=False, nargs='?', const=True, default=False)
    sub.set_defaults(func=get_account)

    sub = subparsers.add_parser("get-transactions")
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--address", required=True)
    sub.set_defaults(func=get_account_transactions)


def setup_parser_validators(subparsers):
    stake_prepare_parser = subparsers.add_parser("stake-prepare")
    stake_prepare_parser.add_argument("--pem", required=True)
    stake_prepare_parser.add_argument("--nonce", required=True)
    stake_prepare_parser.add_argument("--value", default="0")
    stake_prepare_parser.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    stake_prepare_parser.add_argument("--gas-limit", required=True)
    stake_prepare_parser.add_argument("--number-of-nodes", required=True)
    stake_prepare_parser.add_argument("--nodes-public-keys", required=True)
    stake_prepare_parser.add_argument("--reward-address", default="")
    stake_prepare_parser.add_argument("--tag", default="untitled")
    stake_prepare_parser.add_argument("workspace", nargs='?', default=os.getcwd())
    stake_prepare_parser.set_defaults(func=stake_prepare)

    stake_send_parser = subparsers.add_parser("stake-send")
    stake_send_parser.add_argument("tx")
    stake_send_parser.add_argument("--proxy", required=True)
    stake_send_parser.set_defaults(func=stake_send)

    stake_prepare_parser_and_send = subparsers.add_parser("stake")
    stake_prepare_parser_and_send.add_argument("--pem", required=True)
    stake_prepare_parser_and_send.add_argument("--value", default="0")
    stake_prepare_parser_and_send.add_argument("--estimate-gas", action="store_true", default=False)
    stake_prepare_parser_and_send.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    stake_prepare_parser_and_send.add_argument("--gas-limit", required=not("--estimate-gas" in sys.argv))
    stake_prepare_parser_and_send.add_argument("--number-of-nodes", required=True)
    stake_prepare_parser_and_send.add_argument("--nodes-public-keys", required=True)
    stake_prepare_parser_and_send.add_argument("--reward-address", default="")
    stake_prepare_parser_and_send.add_argument("--proxy", required=True)
    stake_prepare_parser_and_send.set_defaults(func=stake_prepare_and_send)

    un_stake_parser = subparsers.add_parser("unstake")
    un_stake_parser.add_argument("--pem", required=True)
    un_stake_parser.add_argument("--value", default="0")
    un_stake_parser.add_argument("--estimate-gas", action="store_true", default=False)
    un_stake_parser.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    un_stake_parser.add_argument("--gas-limit", required=not ("--estimate-gas" in sys.argv))
    un_stake_parser.add_argument("--nodes-public-keys", required=True)
    un_stake_parser.add_argument("--proxy", required=True)
    un_stake_parser.set_defaults(func=do_un_stake)

    un_jail_parser = subparsers.add_parser("unjail")
    un_jail_parser.add_argument("--pem", required=True)
    un_jail_parser.add_argument("--value", default="0")
    un_jail_parser.add_argument("--estimate-gas", action="store_true", default=False)
    un_jail_parser.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    un_jail_parser.add_argument("--gas-limit", required=not ("--estimate-gas" in sys.argv))
    un_jail_parser.add_argument("--nodes-public-keys", required=True)
    un_jail_parser.add_argument("--proxy", required=True)
    un_jail_parser.set_defaults(func=do_un_jail)

    un_bond_parser = subparsers.add_parser("unbond")
    un_bond_parser.add_argument("--pem", required=True)
    un_bond_parser.add_argument("--value", default="0")
    un_bond_parser.add_argument("--estimate-gas", action="store_true", default=False)
    un_bond_parser.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    un_bond_parser.add_argument("--gas-limit", required=not ("--estimate-gas" in sys.argv))
    un_bond_parser.add_argument("--nodes-public-keys", required=True)
    un_bond_parser.add_argument("--proxy", required=True)
    un_bond_parser.set_defaults(func=do_un_bond)

    change_reward_address_parser = subparsers.add_parser("change-reward-address")
    change_reward_address_parser.add_argument("--value", default="0")
    change_reward_address_parser.add_argument("--pem", required=True)
    change_reward_address_parser.add_argument("--estimate-gas", action="store_true", default=False)
    change_reward_address_parser.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    change_reward_address_parser.add_argument("--gas-limit", required=not ("--estimate-gas" in sys.argv))
    change_reward_address_parser.add_argument("--reward-address", required=True)
    change_reward_address_parser.add_argument("--proxy", required=True)
    change_reward_address_parser.set_defaults(func=change_reward_address)

    claim_parser = subparsers.add_parser("claim")
    claim_parser.add_argument("--value", default="0")
    claim_parser.add_argument("--pem", required=True)
    claim_parser.add_argument("--estimate-gas", action="store_true", default=False)
    claim_parser.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    claim_parser.add_argument("--gas-limit", required=not ("--estimate-gas" in sys.argv))
    claim_parser.add_argument("--proxy", required=True)
    claim_parser.set_defaults(func=do_claim)


def setup_parser_wallet(subparsers):
    wallet_parser = subparsers.add_parser("wallet")
    wallet_subparsers = wallet_parser.add_subparsers()

    subparser = wallet_subparsers.add_parser("generate")
    subparser.add_argument("pem")
    subparser.add_argument("--mnemonic", required=False, default="")
    subparser.set_defaults(func=generate_pem)

    subparser = wallet_subparsers.add_parser("bech32")
    subparser.add_argument("value")
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument("--encode", action="store_true")
    group.add_argument("--decode", action="store_true")
    subparser.set_defaults(func=do_bech32)


def setup_parser_cost(subparsers):
    cost_parser = subparsers.add_parser("cost")
    cost_subparsers = cost_parser.add_subparsers()

    get_gas_price_parser = cost_subparsers.add_parser("gas-price")
    get_gas_price_parser.add_argument("--proxy", required=True)
    get_gas_price_parser.set_defaults(func=get_gas_price)

    get_transaction_cost_parser = cost_subparsers.add_parser("transaction")
    tx_types = [proxy.TxTypes.SC_CALL, proxy.TxTypes.MOVE_BALANCE, proxy.TxTypes.SC_DEPLOY]
    get_transaction_cost_parser.add_argument("tx_type", choices=tx_types)
    get_transaction_cost_parser.add_argument("--proxy", required=True)
    get_transaction_cost_parser.add_argument("--data", required=False)
    get_transaction_cost_parser.add_argument("--sc-address", required=False)
    get_transaction_cost_parser.add_argument("--sc-path", required=False)
    get_transaction_cost_parser.add_argument("--function", required=False)
    get_transaction_cost_parser.add_argument("--arguments", nargs='+', required=False)
    get_transaction_cost_parser.set_defaults(func=get_transaction_cost)


def setup_parser_network(subparsers):
    network_parser = subparsers.add_parser("network")
    network_subparsers = network_parser.add_subparsers()

    subparser = network_subparsers.add_parser("num-shards")
    subparser.add_argument("--proxy", required=True)
    subparser.set_defaults(func=get_num_shards)

    subparser = network_subparsers.add_parser("last-block-nonce")
    subparser.add_argument("--proxy", required=True)
    subparser.add_argument("--shard-id", required=True)
    subparser.set_defaults(func=get_last_block_nonce)

    subparser = network_subparsers.add_parser("chain-id")
    subparser.add_argument("--proxy", required=True)
    subparser.set_defaults(func=get_chain_id)

    subparser = network_subparsers.add_parser("meta-nonce")
    subparser.add_argument("--proxy", required=True)
    subparser.set_defaults(func=get_meta_nonce)

    subparser = network_subparsers.add_parser("meta-block")
    subparser.add_argument("--proxy", required=True)
    subparser.add_argument("--nonce", required=True, type=int)
    subparser.set_defaults(func=get_meta_block)


def setup_parser_blockatlas(subparsers):
    parser = subparsers.add_parser("blockatlas")
    subparsers = parser.add_subparsers()

    parser.add_argument("--url", required=True)
    parser.add_argument("--coin", required=True)

    sub = subparsers.add_parser("current-block-number")
    sub.set_defaults(func=facade.blockatlas_get_current_block_number)

    sub = subparsers.add_parser("block-by-number")
    sub.add_argument("--number", required=True)
    sub.set_defaults(func=facade.blockatlas_get_block_by_number)

    sub = subparsers.add_parser("transactions")
    sub.add_argument("--address", required=True)
    sub.set_defaults(func=facade.blockatlas_get_txs_by_address)


def setup_parser_queue(subparsers):
    parser = subparsers.add_parser("dispatcher")
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("enqueue")
    sub.add_argument("--value", default="0")
    sub.add_argument("--receiver", required=True)
    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    sub.add_argument("--gas-limit", required=True)
    sub.add_argument("--data", default="")
    sub.set_defaults(func=enqueue_transaction)

    sub = subparsers.add_parser("dispatch")
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--pem", required=True)
    sub.set_defaults(func=dispatch_transactions)

    sub = subparsers.add_parser("dispatch-continuously")
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--pem", required=True)
    sub.add_argument("--interval", required=True)
    sub.set_defaults(func=dispatch_transactions_continuously)

    sub = subparsers.add_parser("clean")
    sub.set_defaults(func=clean_transactions_queue)


def get_account(args):
    if args.balance:
        facade.get_account_balance(args)
    elif args.nonce:
        facade.get_account_nonce(args)
    else:
        facade.get_account(args)


def get_account_transactions(args):
    facade.get_account_transactions(args)


def get_transaction_cost(args):
    facade.get_transaction_cost(args)


def get_num_shards(args):
    facade.get_num_shards(args)


def get_last_block_nonce(args):
    facade.get_last_block_nonce(args)


def get_gas_price(args):
    facade.get_gas_price(args)


def get_chain_id(args):
    facade.get_chain_id(args)


def get_meta_nonce(args):
    facade.get_meta_nonce(args)


def get_meta_block(args):
    facade.get_meta_block(args)


def tx_prepare(args):
    transactions.prepare(args)


def tx_send(args):
    facade.send_prepared_transaction(args)


def tx_prepare_and_send(args):
    facade.prepare_and_send_transaction(args)


def generate_pem(args):
    facade.generate_pem(args)


def do_bech32(args):
    facade.do_bech32(args)


def stake_prepare(args):
    transactions.stake_prepare(args)


def stake_send(args):
    facade.send_prepared_transaction(args)


def stake_prepare_and_send(args):
    facade.prepare_and_send_stake_transaction(args)


def do_un_stake(args):
    facade.prepare_and_send_un_stake_transaction(args)


def do_un_bond(args):
    facade.prepare_and_send_un_bond_transaction(args)


def do_un_jail(args):
    facade.prepare_and_send_un_jail_transaction(args)


def change_reward_address(args):
    facade.prepare_and_send_change_reward_address_transaction(args)


def do_claim(args):
    facade.prepare_and_send_claim_transaction(args)


def enqueue_transaction(args):
    facade.enqueue_transaction(args)


def dispatch_transactions(args):
    facade.dispatch_transactions(args)


def dispatch_transactions_continuously(args):
    facade.dispatch_transactions_continuously(args)


def clean_transactions_queue(args):
    facade.clean_transactions_queue()


if __name__ == "__main__":
    main()
