import logging
from typing import Any

from erdpy import cli_shared, utils
from erdpy.accounts import Address
from erdpy.proxy.core import ElrondProxy

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
    cli_shared.add_omit_fields_arg(sub)
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
    proxy_url = args.proxy
    address = args.address
    proxy = ElrondProxy(proxy_url)
    account = proxy.get_account(Address(address))
    omit_fields = cli_shared.parse_omit_fields_arg(args)

    if args.balance:
        print(account.get("balance", 0))
    elif args.nonce:
        print(account.get("nonce", 0))
    else:
        utils.omit_fields(account, omit_fields)
        utils.dump_out_json(account)


def get_account_transactions(args: Any):
    proxy_url = args.proxy
    address = args.address
    proxy = ElrondProxy(proxy_url)

    response = proxy.get_account_transactions(Address(address))
    utils.dump_out_json(response, args.outfile)
