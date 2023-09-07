import getpass
import json
import logging
import sys
from pathlib import Path
from typing import Any, List, Optional, Tuple

from multiversx_sdk_core import Address
from multiversx_sdk_wallet import UserSecretKey, UserWallet
from multiversx_sdk_wallet.mnemonic import Mnemonic
from multiversx_sdk_wallet.user_pem import UserPEM

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.constants import DEFAULT_HRP
from multiversx_sdk_cli.errors import KnownError

logger = logging.getLogger("cli.wallet")

WALLET_FORMAT_RAW_MNEMONIC = "raw-mnemonic"
WALLET_FORMAT_KEYSTORE_MNEMONIC = "keystore-mnemonic"
WALLET_FORMAT_KEYSTORE_SECRET_KEY = "keystore-secret-key"
WALLET_FORMAT_PEM = "pem"
WALLET_FORMAT_ADDRESS_BECH32 = "address-bech32"
WALLET_FORMAT_ADDRESS_HEX = "address-hex"

WALLET_FORMATS = [
    WALLET_FORMAT_RAW_MNEMONIC,
    WALLET_FORMAT_KEYSTORE_MNEMONIC,
    WALLET_FORMAT_KEYSTORE_SECRET_KEY,
    WALLET_FORMAT_PEM,
]

WALLET_FORMATS_AND_ADDRESSES = [*WALLET_FORMATS, WALLET_FORMAT_ADDRESS_BECH32, WALLET_FORMAT_ADDRESS_HEX]


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
    sub.add_argument("--format", choices=WALLET_FORMATS, help="the format of the generated wallet file (default: %(default)s)", default=None)
    sub.add_argument("--outfile", help="the output path and base file name for the generated wallet files (default: %(default)s)", type=str)
    sub.add_argument("--address-hrp", help=f"the human-readable part of the address, when format is {WALLET_FORMAT_KEYSTORE_SECRET_KEY} or {WALLET_FORMAT_PEM} (default: %(default)s)", type=str, default=DEFAULT_HRP)
    sub.set_defaults(func=wallet_new)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "wallet",
        "convert",
        "Convert a wallet from one format to another"
    )
    sub.add_argument("--infile", help="path to the input file")
    sub.add_argument("--outfile", help="path to the output file")
    sub.add_argument("--in-format", required=True, choices=WALLET_FORMATS, help="the format of the input file")
    sub.add_argument("--out-format", required=True, choices=WALLET_FORMATS_AND_ADDRESSES, help="the format of the output file")
    sub.add_argument("--address-index", help=f"the address index, if input format is {WALLET_FORMAT_RAW_MNEMONIC}, {WALLET_FORMAT_KEYSTORE_MNEMONIC} or {WALLET_FORMAT_PEM} (with multiple entries) and the output format is {WALLET_FORMAT_KEYSTORE_SECRET_KEY} or {WALLET_FORMAT_PEM}", type=int, default=0)
    sub.add_argument("--address-hrp", help=f"the human-readable part of the address, when the output format is {WALLET_FORMAT_KEYSTORE_SECRET_KEY} or {WALLET_FORMAT_PEM} (default: %(default)s)", type=str, default=DEFAULT_HRP)
    sub.set_defaults(func=convert_wallet)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "wallet",
        "bech32",
        "Helper for encoding and decoding bech32 addresses"
    )
    sub.add_argument("value", help="the value to encode or decode")
    group = sub.add_mutually_exclusive_group(required=True)
    group.add_argument("--encode", action="store_true", help="whether to encode")
    group.add_argument("--decode", action="store_true", help="whether to decode")
    sub.set_defaults(func=do_bech32)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def wallet_new(args: Any):
    format = args.format
    outfile = args.outfile
    address_hrp = args.address_hrp

    mnemonic = Mnemonic.generate()
    print(f"Mnemonic: {mnemonic.get_text()}")

    if format is None:
        return
    if outfile is None:
        raise KnownError("The --outfile option is required when --format is specified.")

    outfile = Path(outfile).expanduser().resolve()
    if outfile.exists():
        raise KnownError(f"File already exists, will not overwrite: {outfile}")

    if format == WALLET_FORMAT_RAW_MNEMONIC:
        outfile.write_text(mnemonic.get_text())
    elif format == WALLET_FORMAT_KEYSTORE_MNEMONIC:
        password = getpass.getpass("Enter a new password (for keystore):")
        wallet = UserWallet.from_mnemonic(mnemonic.get_text(), password)
        wallet.save(outfile)
    elif format == WALLET_FORMAT_KEYSTORE_SECRET_KEY:
        password = getpass.getpass("Enter a new password (for keystore):")
        secret_key = mnemonic.derive_key()
        wallet = UserWallet.from_secret_key(secret_key, password)
        wallet.save(outfile, address_hrp)
    elif format == WALLET_FORMAT_PEM:
        secret_key = mnemonic.derive_key()
        pubkey = secret_key.generate_public_key()
        address = pubkey.to_address(address_hrp)
        pem_file = UserPEM(address.bech32(), secret_key)
        pem_file.save(outfile)
    else:
        raise KnownError(f"Unknown format: {format}")

    logger.info(f"Wallet ({format}) saved: {outfile}")


def convert_wallet(args: Any):
    infile = Path(args.infile).expanduser().resolve() if args.infile else None
    outfile = Path(args.outfile).expanduser().resolve() if args.outfile else None
    in_format = args.in_format
    out_format = args.out_format
    address_index = args.address_index
    address_hrp = args.address_hrp

    if outfile and outfile.exists():
        raise KnownError(f"File already exists, will not overwrite: {outfile}")

    if infile:
        input_text = infile.read_text()
    else:
        print(f"Insert text below. Press 'Ctrl-D' (Linux / MacOS) or 'Ctrl-Z' (Windows) when done.")
        input_text = sys.stdin.read().strip()

    mnemonic, secret_key = _load_wallet(input_text, in_format, address_index)
    output_text = _create_wallet_content(out_format, mnemonic, secret_key, address_index, address_hrp)

    if outfile:
        outfile.write_text(output_text)
    else:
        print("Output:")
        print()
        print(output_text)


def _load_wallet(input_text: str, in_format: str, address_index: int) -> Tuple[Optional[Mnemonic], Optional[UserSecretKey]]:
    if in_format == WALLET_FORMAT_RAW_MNEMONIC:
        input_text = " ".join(input_text.split())
        mnemonic = Mnemonic(input_text)
        return mnemonic, None

    if in_format == WALLET_FORMAT_KEYSTORE_MNEMONIC:
        password = getpass.getpass("Enter the password for the input keystore:")
        keyfile = json.loads(input_text)
        mnemonic = UserWallet.decrypt_mnemonic(keyfile, password)
        return mnemonic, None

    if in_format == WALLET_FORMAT_KEYSTORE_SECRET_KEY:
        password = getpass.getpass("Enter the password for the input keystore:")
        keyfile = json.loads(input_text)
        secret_key = UserWallet.decrypt_secret_key(keyfile, password)
        return None, secret_key

    if in_format == WALLET_FORMAT_PEM:
        secret_key = UserPEM.from_text(input_text, address_index).secret_key
        return None, secret_key

    raise KnownError(f"Cannot load wallet, unknown input format: <{in_format}>. Make sure to use one of following: {WALLET_FORMATS}.")


def _create_wallet_content(
        out_format: str,
        mnemonic: Optional[Mnemonic],
        secret_key: Optional[UserSecretKey],
        address_index: int,
        address_hrp: str
) -> str:
    if out_format == WALLET_FORMAT_RAW_MNEMONIC:
        if mnemonic is None:
            raise KnownError(f"Cannot convert to {out_format} (mnemonic not available).")
        return mnemonic.get_text()

    if out_format == WALLET_FORMAT_KEYSTORE_MNEMONIC:
        if mnemonic is None:
            raise KnownError(f"Cannot convert to {out_format} (mnemonic not available).")

        password = getpass.getpass("Enter a new password (for the output keystore):")
        wallet = UserWallet.from_mnemonic(mnemonic.get_text(), password)
        return wallet.to_json()

    if out_format == WALLET_FORMAT_KEYSTORE_SECRET_KEY:
        if mnemonic:
            secret_key = mnemonic.derive_key(address_index)
        assert secret_key is not None

        password = getpass.getpass("Enter a new password (for the output keystore):")
        wallet = UserWallet.from_secret_key(secret_key, password)
        return wallet.to_json(address_hrp)

    if out_format == WALLET_FORMAT_PEM:
        if mnemonic:
            secret_key = mnemonic.derive_key(address_index)
        assert secret_key is not None

        pubkey = secret_key.generate_public_key()
        address = pubkey.to_address(address_hrp)
        pem = UserPEM(address.bech32(), secret_key)
        return pem.to_text()

    if out_format == WALLET_FORMAT_ADDRESS_BECH32:
        if mnemonic:
            secret_key = mnemonic.derive_key(address_index)
        assert secret_key is not None

        pubkey = secret_key.generate_public_key()
        address = pubkey.to_address(address_hrp)
        return address.bech32()

    if out_format == WALLET_FORMAT_ADDRESS_HEX:
        if mnemonic:
            secret_key = mnemonic.derive_key(address_index)
        assert secret_key is not None

        pubkey = secret_key.generate_public_key()
        return pubkey.hex()

    raise KnownError(f"Cannot create wallet, unknown output format: <{out_format}>. Make sure to use one of following: {WALLET_FORMATS}.")


def do_bech32(args: Any):
    encode = args.encode
    value = args.value

    if encode:
        address = Address.from_hex(value, DEFAULT_HRP)
        result = address.bech32()
    else:
        address = Address.from_bech32(value)
        result = address.hex()

    print(result)
    return result
