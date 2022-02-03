from erdpy.wallet.keyfile import save_to_key_file
from erdpy.wallet.core import generate_mnemonic
import logging
import getpass
from pathlib import Path
from typing import Any, List

from erdpy import cli_shared, wallet, utils
from erdpy.accounts import Account, Address
from erdpy.wallet import pem

logger = logging.getLogger("cli.wallet")


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers,
        "wallet",
        "Create wallet, derive secret key from mnemonic, bech32 address helpers etc."
    )
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(
        subparsers,
        "wallet",
        "new",
        "Create a new wallet and print its mnemonic; optionally save as password-protected JSON (recommended) or PEM (not recommended)"
    )
    sub.add_argument("--json",
                     help="whether to create a json key file", action="store_true", default=False)
    sub.add_argument("--pem",
                     help="whether to create a pem key file", action="store_true", default=False)
    sub.add_argument("--output-path",
                     help="the output path and base file name for the generated wallet files (default: %(default)s)", type=str, default="./wallet")
    sub.set_defaults(func=new_wallet)

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

    sub = cli_shared.add_command_subparser(
        subparsers,
        "wallet",
        "pem-address",
        "Get the public address out of a PEM file as bech32"
    )
    sub.add_argument("pem", help="path to the PEM file")
    sub.add_argument("--pem-index", default=0, help="🔑 the index in the PEM file (default: %(default)s)")
    sub.set_defaults(func=pem_address)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "wallet",
        "pem-address-hex",
        "Get the public address out of a PEM file as hex"
    )
    sub.add_argument("pem", help="path to the PEM file")
    sub.add_argument("--pem-index", default=0, help="🔑 the index in the PEM file (default: %(default)s)")
    sub.set_defaults(func=pem_address_hex)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def new_wallet(args: Any):
    mnemonic = generate_mnemonic()
    print(f"Mnemonic: {mnemonic}")
    secret_key, pubkey = wallet.derive_keys(mnemonic)
    if args.pem:
        pem_file = prepare_file(args.output_path, ".pem")
        address = Address(pubkey)
        pem.write(pem_file, secret_key, pubkey, name=address.bech32())
        logger.info(f"Pem wallet generated: {pem_file}")
    if args.json:
        json_file = prepare_file(args.output_path, ".json")
        password = getpass.getpass("Enter a new password:")
        save_to_key_file(json_file, secret_key, pubkey, password)
        logger.info(f"Json wallet generated: {json_file}")


def prepare_file(output_path: str, suffix: str) -> Path:
    base_path = Path(output_path)
    utils.ensure_folder(base_path.parent)
    file_path = base_path.with_suffix(suffix)
    return utils.uniquify(file_path)


def generate_pem(args: Any):
    pem_file = Path(args.pem)
    mnemonic = args.mnemonic
    index = args.index

    secret_key, pubkey = wallet.generate_pair()
    if mnemonic:
        mnemonic = input("Enter mnemonic:\n")
        mnemonic = mnemonic.strip()
        secret_key, pubkey = wallet.derive_keys(mnemonic, index)

    address = Address(pubkey)
    pem.write(pem_file, secret_key, pubkey, name=address.bech32())
    logger.info(f"Created PEM file [{pem_file}] for [{address.bech32()}]")


def do_bech32(args: Any):
    encode = args.encode
    value = args.value
    address = Address(value)

    result = address.bech32() if encode else address.hex()
    print(result)
    return result


def pem_address(args: Any):
    account = Account(pem_file=args.pem, pem_index=args.pem_index)
    print(account.address)


def pem_address_hex(args: Any):
    account = Account(pem_file=args.pem, pem_index=args.pem_index)
    print(account.address.hex())
