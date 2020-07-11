import logging
from typing import Any

from erdpy import facade, proxy

logger = logging.getLogger("cli.cost")


def setup_parser(subparsers: Any) -> Any:
    cost_parser = subparsers.add_parser("cost", description="Estimate cost of Transactions")
    cost_subparsers = cost_parser.add_subparsers()

    sub = cost_subparsers.add_parser("gas-price")
    sub.add_argument("--proxy", required=True)
    sub.set_defaults(func=get_gas_price)

    sub = cost_subparsers.add_parser("transaction")
    tx_types = [proxy.TxTypes.SC_CALL, proxy.TxTypes.MOVE_BALANCE, proxy.TxTypes.SC_DEPLOY]
    sub.add_argument("type", choices=tx_types)
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--data", required=False)
    sub.add_argument("--sc-address", required=False)
    sub.add_argument("--sc-path", required=False)
    sub.add_argument("--function", required=False)
    sub.add_argument("--arguments", nargs='+', required=False)
    sub.set_defaults(func=get_transaction_cost)

    return subparsers


def get_transaction_cost(args):
    facade.get_transaction_cost(args)


def get_gas_price(args):
    facade.get_gas_price(args)
