import logging

from erdpy import facade

logger = logging.getLogger("cli.accounts")


def setup_parser(subparsers):
    parser = subparsers.add_parser("account")
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("get")
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--address", required=True)
    sub.add_argument("--balance", required=False, nargs='?', const=True, default=False)
    sub.add_argument("--nonce", required=False, nargs='?', const=True, default=False)
    sub.set_defaults(func=get_account)

    sub = subparsers.add_parser("get-transactions")
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--address", required=True)
    sub.set_defaults(func=get_account_transactions)


def get_account(args):
    if args.balance:
        facade.get_account_balance(args)
    elif args.nonce:
        facade.get_account_nonce(args)
    else:
        facade.get_account(args)


def get_account_transactions(args):
    facade.get_account_transactions(args)
