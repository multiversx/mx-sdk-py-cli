import os
import sys

from erdpy import config, facade, transactions


def setup_parser(subparsers):
    sub = subparsers.add_parser("tx-prepare")
    _add_common_arguments(sub)
    sub.add_argument("--tag", default="untitled")
    sub.add_argument("workspace", nargs='?', default=os.getcwd())
    sub.set_defaults(func=tx_prepare)

    sub = subparsers.add_parser("tx-send")
    sub.add_argument("tx")
    sub.add_argument("--proxy", required=True)
    sub.set_defaults(func=tx_send)

    sub = subparsers.add_parser("tx-prepare-and-send")
    _add_common_arguments(sub)
    sub.add_argument("--proxy", required=True)
    sub.set_defaults(func=tx_prepare_and_send)


def _add_common_arguments(sub):
    sub.add_argument("--pem", required=True)
    sub.add_argument("--nonce", type=int, required=not("--recall-nonce" in sys.argv))
    sub.add_argument("--recall-nonce", action="store_true", default=False)
    sub.add_argument("--value", default="0")
    sub.add_argument("--receiver", required=True)
    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    sub.add_argument("--gas-limit", required=True)
    sub.add_argument("--data", default="")


def tx_prepare(args):
    transactions.prepare(args)


def tx_send(args):
    facade.send_prepared_transaction(args)


def tx_prepare_and_send(args):
    facade.prepare_and_send_transaction(args)
