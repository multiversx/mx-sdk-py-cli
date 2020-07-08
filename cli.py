import logging
import sys
from argparse import ArgumentParser

from erdpy import (cli_accounts, cli_blockatlas, cli_config, cli_contracts,
                   cli_cost, cli_dispatcher, cli_deps, cli_network,
                   cli_transactions, cli_validators, cli_wallet, errors)
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
    cli_deps.setup_parser(subparsers)
    cli_contracts.setup_parser(subparsers)
    cli_validators.setup_parser(subparsers)
    cli_transactions.setup_parser(subparsers)
    cli_accounts.setup_parser(subparsers)
    cli_wallet.setup_parser(subparsers)
    cli_network.setup_parser(subparsers)
    cli_cost.setup_parser(subparsers)
    cli_dispatcher.setup_parser(subparsers)
    cli_blockatlas.setup_parser(subparsers)

    return parser


if __name__ == "__main__":
    main()
