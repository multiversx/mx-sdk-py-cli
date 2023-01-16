import logging
from typing import Any

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.ledger.ledger_app_handler import LedgerApp

logger = logging.getLogger("cli.ledger")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "ledger", "Get Ledger App addresses and version")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "ledger", "addresses", "Get the addresses within Ledger")
    sub.add_argument("--num-addresses", required=False, type=int, default=10, help="The number of addresses to fetch")
    sub.set_defaults(func=print_addresses)

    sub = cli_shared.add_command_subparser(subparsers, "ledger", "version", "Get the version of the MultiversX App for Ledger")
    sub.set_defaults(func=print_version)

    return subparsers


def print_addresses(args: Any):
    ledger_app = LedgerApp()
    for i in range(args.num_addresses):
        address = ledger_app.get_address(0, i)
        print('account index = %d | address index = %d | address: %s' % (0, i, address))
    ledger_app.close()


def print_version(args: Any):
    ledger_app = LedgerApp()
    print("MultiversX App version: " + ledger_app.get_version())
    ledger_app.close()
