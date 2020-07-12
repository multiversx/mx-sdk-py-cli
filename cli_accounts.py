from erdpy import cli_shared
import logging
from typing import Any

from erdpy import facade

logger = logging.getLogger("cli.accounts")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "account", "Get Account data (nonce, balance) from the Network")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "account", "get", "Query account details (nonce, balance etc.)")
    cli_shared.add_proxy_arg(sub)
    _add_address_arg(sub)
    mutex = sub.add_mutually_exclusive_group()
    mutex.add_argument("--balance", action="store_true", help="whether to only fetch the balance")
    mutex.add_argument("--nonce", action="store_true", help="whether to only fetch the nonce")
    sub.set_defaults(func=get_account)

    sub = cli_shared.add_command_subparser(subparsers, "account", "get-transactions", "Query account transactions")
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_outfile_arg(sub)
    _add_address_arg(sub)
    sub.set_defaults(func=get_account_transactions)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_address_arg(sub: Any):
    sub.add_argument("--address", required=True, help="🖄 the address to query")


def get_account(args: Any):
    if args.balance:
        facade.get_account_balance(args)
    elif args.nonce:
        facade.get_account_nonce(args)
    else:
        facade.get_account(args)


def get_account_transactions(args: Any):
    facade.get_account_transactions(args)
