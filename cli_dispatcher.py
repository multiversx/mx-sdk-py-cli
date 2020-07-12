import logging
from typing import Any

from erdpy import cli_shared, config, facade

logger = logging.getLogger("cli.dispatcher")


def setup_parser(subparsers: Any) -> Any:
    parser = subparsers.add_parser("dispatcher", description="Enqueue transactions, then bulk dispatch them")
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("enqueue")
    sub.add_argument("--value", default="0")
    sub.add_argument("--receiver", required=True)
    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    sub.add_argument("--gas-limit", required=True)
    sub.add_argument("--data", default="")
    sub.add_argument("--chain", default=config.get_chain_id())
    sub.add_argument("--version", default=config.get_tx_version())
    sub.set_defaults(func=enqueue_transaction)

    sub = subparsers.add_parser("dispatch")
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_wallet_args(sub)
    sub.set_defaults(func=dispatch_transactions)

    sub = subparsers.add_parser("dispatch-continuously")
    cli_shared.add_proxy_arg(sub)
    sub.add_argument("--interval", required=True)
    cli_shared.add_wallet_args(sub)
    sub.set_defaults(func=dispatch_transactions_continuously)

    sub = subparsers.add_parser("clean")
    sub.set_defaults(func=clean_transactions_queue)

    return subparsers


def enqueue_transaction(args: Any):
    facade.enqueue_transaction(args)


def dispatch_transactions(args: Any):
    facade.dispatch_transactions(args)


def dispatch_transactions_continuously(args: Any):
    facade.dispatch_transactions_continuously(args)


def clean_transactions_queue(args: Any):
    facade.clean_transactions_queue()
