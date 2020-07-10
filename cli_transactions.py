import os
import sys
from argparse import FileType

from erdpy import config, facade, transactions
from erdpy.utils import is_arg_present


def setup_parser(subparsers):
    # DEPRECATED
    sub = subparsers.add_parser("tx-prepare")
    _add_common_arguments(sub)
    sub.add_argument("--tag", default="untitled")
    sub.add_argument("workspace", nargs='?', default=os.getcwd())
    sub.set_defaults(func=tx_prepare)

    # DEPRECATED
    sub = subparsers.add_parser("tx-send")
    sub.add_argument("tx")
    sub.add_argument("--proxy", required=True)
    sub.set_defaults(func=tx_send)

    # DEPRECATED
    sub = subparsers.add_parser("tx-prepare-and-send")
    _add_common_arguments(sub)
    sub.add_argument("--proxy", required=True)
    sub.set_defaults(func=tx_prepare_and_send)

    # NEW API
    parser = subparsers.add_parser("tx")
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("new", description="Create a new regular transaction")
    _add_common_arguments(sub)
    sub.add_argument("--outfile", type=FileType("w"), default=sys.stdout, help="where to save the signed transaction, "
                                                                               "the hash")
    sub.add_argument("--send", action="store_true", default=False)
    sub.add_argument("--proxy", default=config.get_proxy())
    sub.set_defaults(func=create_transaction)

    sub = subparsers.add_parser("send", description="Send a previously saved transaction")
    sub.add_argument("--infile", type=FileType("r"), default=None, help="a previously saved transaction")
    sub.add_argument("--outfile", type=FileType("w"), default=sys.stdout, help="where to save the output (the hash)")
    sub.add_argument("--proxy", default=config.get_proxy())
    sub.set_defaults(func=send_transaction)


def _add_common_arguments(sub):
    sub.add_argument("--pem", required=not(is_arg_present("--keyfile", sys.argv)))
    sub.add_argument("--keyfile", required=not(is_arg_present("--pem", sys.argv)))
    sub.add_argument("--passfile", required=not(is_arg_present("--pem", sys.argv)))

    sub.add_argument("--nonce", type=int, required=not("--recall-nonce" in sys.argv))
    sub.add_argument("--recall-nonce", action="store_true", default=False)
    sub.add_argument("--value", default="0")
    sub.add_argument("--receiver", required=True)
    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    sub.add_argument("--gas-limit", required=True)
    sub.add_argument("--data", default="")
    sub.add_argument("--data-file", type=FileType("r"), default=None, help="a file containing transaction data")
    sub.add_argument("--chain", default=config.get_chain_id())
    sub.add_argument("--version", type=int, default=config.get_tx_version())


def tx_prepare(args):
    transactions.prepare(args)


def tx_send(args):
    facade.send_prepared_transaction(args)


def tx_prepare_and_send(args):
    facade.prepare_and_send_transaction(args)


def create_transaction(args):
    facade.create_transaction(args)


def send_transaction(args):
    facade.send_transaction(args)
