import logging
import sys
from argparse import ArgumentParser

from erdpy import (cli_accounts, cli_blockatlas, cli_config, cli_contracts,
                   cli_cost, cli_install, cli_network, cli_transactions,
                   cli_validators, cli_wallet, config, errors, facade)
from erdpy._version import __version__

logger = logging.getLogger("cli")


def main():
    try:
        _do_main()
    except errors.KnownError as err:
        logger.fatal(err.get_pretty())
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

    cli_config.setup_parser(subparsers)
    cli_install.setup_parser(subparsers)
    cli_contracts.setup_parser(subparsers)
    cli_validators.setup_parser(subparsers)
    cli_transactions.setup_parser(subparsers)
    cli_accounts.setup_parser(subparsers)
    cli_wallet.setup_parser(subparsers)
    cli_network.setup_parser(subparsers)
    cli_cost.setup_parser(subparsers)
    cli_blockatlas.setup_parser(subparsers)

    setup_parser_dispatcher(subparsers)

    return parser


def setup_parser_dispatcher(subparsers):
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
