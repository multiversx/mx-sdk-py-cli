import logging
from typing import Any

from erdpy import cli_shared, wallet
from erdpy.accounts import Address
from erdpy.wallet import pem

logger = logging.getLogger("cli.wallet")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers,
        "wallet",
        "Derive private key from mnemonic, bech32 address helpers etc."
    )
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(
        subparsers,
        "wallet",
        "derive",
        "Derive a PEM file from a mnemonic or generate a new PEM file (for tests only!)"
    )
    sub.add_argument("pem",
                     help="path of the output PEM file")
    sub.add_argument("--mnemonic", action="store_true",
                     help="whether to derive from an existing mnemonic")
    sub.add_argument("--index",
                     help="the account index", type=int, default=0)
    sub.set_defaults(func=generate_pem)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "wallet",
        "bech32",
        "Helper for encoding and decoding bech32 addresses"
    )
    sub.add_argument("value",
                     help="the value to encode or decode")
    group = sub.add_mutually_exclusive_group(required=True)
    group.add_argument("--encode", action="store_true",
                       help="whether to encode")
    group.add_argument("--decode", action="store_true",
                       help="whether to decode")
    sub.set_defaults(func=do_bech32)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def generate_pem(args: Any):
    pem_file = args.pem
    mnemonic = args.mnemonic
    index = args.index

    seed, pubkey = wallet.generate_pair()
    if mnemonic:
        mnemonic = input("Enter mnemonic:\n")
        mnemonic = mnemonic.strip()
        seed, pubkey = wallet.derive_keys(mnemonic, index)

    address = Address(pubkey)
    pem.write(pem_file, seed, pubkey, name=address.bech32())
    logger.info(f"Created PEM file [{pem_file}] for [{address.bech32()}]")


def do_bech32(args: Any):
    encode = args.encode
    value = args.value
    address = Address(value)

    result = address.bech32() if encode else address.hex()
    print(result)
    return result
