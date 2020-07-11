
import logging
from typing import Any

from erdpy import facade

logger = logging.getLogger("cli.wallet")


def setup_parser(subparsers: Any) -> Any:
    wallet_parser = subparsers.add_parser("wallet", description="Derive private key from mnemonic, bech32 address helpers etc.")
    wallet_subparsers = wallet_parser.add_subparsers()

    subparser = wallet_subparsers.add_parser("generate")
    subparser.add_argument("pem")
    subparser.add_argument("--mnemonic", action="store_true")
    subparser.set_defaults(func=generate_pem)

    subparser = wallet_subparsers.add_parser("bech32")
    subparser.add_argument("value")
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument("--encode", action="store_true")
    group.add_argument("--decode", action="store_true")
    subparser.set_defaults(func=do_bech32)

    return subparsers


def generate_pem(args: Any):
    facade.generate_pem(args)


def do_bech32(args: Any):
    facade.do_bech32(args)
