import logging
import sys

from erdpy import config, facade
from erdpy.utils import is_arg_present

logger = logging.getLogger("cli.dispatcher")


def setup_parser(subparsers):
    parser = subparsers.add_parser("dispatcher")
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
    sub.add_argument("--proxy", required=True)

    sub.add_argument("--pem", required=not(is_arg_present("--keyfile", sys.argv)))
    sub.add_argument("--keyfile", required=not(is_arg_present("--pem", sys.argv)))
    sub.add_argument("--passfile", required=not(is_arg_present("--pem", sys.argv)))

    sub.set_defaults(func=dispatch_transactions)

    sub = subparsers.add_parser("dispatch-continuously")
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--pem", required=True)
    sub.add_argument("--interval", required=True)
    sub.set_defaults(func=dispatch_transactions_continuously)

    sub = subparsers.add_parser("clean")
    sub.set_defaults(func=clean_transactions_queue)


def enqueue_transaction(args):
    facade.enqueue_transaction(args)


def dispatch_transactions(args):
    facade.dispatch_transactions(args)


def dispatch_transactions_continuously(args):
    facade.dispatch_transactions_continuously(args)


def clean_transactions_queue(args):
    facade.clean_transactions_queue()
