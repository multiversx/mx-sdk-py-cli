import getpass
import json
import logging
from pathlib import Path
from typing import Any, List, Optional

from multiversx_sdk_wallet import UserSecretKey, UserWallet
from multiversx_sdk_wallet.mnemonic import Mnemonic
from multiversx_sdk_wallet.user_pem import UserPEM

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.accounts import Account, Address

logger = logging.getLogger("cli.wallet")

WALLET_FORMAT_RAW_MNEMONIC = "raw-mnemonic"
WALLET_FORMAT_KEYSTORE_MNEMONIC = "keystore-mnemonic"
WALLET_FORMAT_KEYSTORE_SECRET_KEY = "keystore-secret-key"
WALLET_FORMAT_PEM = "pem"
WALLET_FORMATS = [
    WALLET_FORMAT_RAW_MNEMONIC,
    WALLET_FORMAT_KEYSTORE_MNEMONIC,
    WALLET_FORMAT_KEYSTORE_SECRET_KEY,
    WALLET_FORMAT_PEM,
]


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
    sub.add_argument("--json", help="DEPRECATED, replaced by --format=keystore-mnemonic", action="store_true", default=False)
    sub.add_argument("--pem", help="DEPRECATED, replaced by --format=pem", action="store_true", default=False)
    sub.add_argument("--output-path", help="DEPRECATED, replaced by --outfile", type=str)
    sub.add_argument("--format", choices=WALLET_FORMATS, help="the format of the generated wallet file (default: %(default)s)", default=None)
    sub.add_argument("--outfile", help="the output path and base file name for the generated wallet files (default: %(default)s)", type=str)
    sub.add_argument("--address-hrp", help=f"the human-readable part of the address, when format is {WALLET_FORMAT_KEYSTORE_SECRET_KEY} or {WALLET_FORMAT_PEM} (default: %(default)s)", type=str, default="erd")
    sub.set_defaults(func=new_wallet)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "wallet",
        "derive",
        "DEPRECATED COMMAND, replaced by 'wallet convert'"
    )
    sub.add_argument("pem", help="path of the output PEM file")
    sub.add_argument("--mnemonic", action="store_true", help="whether to derive from an existing mnemonic")
    sub.add_argument("--index", help="the address index", type=int, default=0)
    sub.set_defaults(func=generate_pem)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "wallet",
        "convert",
        "Convert a wallet from one format to another"
    )

    sub.add_argument("--infile", required=True, help="path to the input file")
    sub.add_argument("--outfile", required=True, help="path to the output file")
    sub.add_argument("--in-format", required=True, choices=WALLET_FORMATS, help="the format of the input file")
    sub.add_argument("--out-format", required=True, choices=WALLET_FORMATS, help="the format of the output file")
    sub.add_argument("--address-index", help=f"the address index, if input format is {WALLET_FORMAT_RAW_MNEMONIC}, {WALLET_FORMAT_KEYSTORE_MNEMONIC} or {WALLET_FORMAT_PEM} (with multiple entries) and the output format is {WALLET_FORMAT_KEYSTORE_SECRET_KEY} or {WALLET_FORMAT_PEM}", type=int, default=0)
    sub.add_argument("--address-hrp", help=f"the human-readable part of the address, when the output format is {WALLET_FORMAT_KEYSTORE_SECRET_KEY} or {WALLET_FORMAT_PEM} (default: %(default)s)", type=str, default="erd")
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
    format = args.format
    outfile = args.outfile
    address_hrp = args.address_hrp

    # Handle deprecated options
    if args.json:
        logger.warning("The --json option is deprecated, use --format=keystore-mnemonic instead.")
        format = "keystore-mnemonic"
    if args.pem:
        logger.warning("The --pem option is deprecated, use --format=pem instead.")
        format = "pem"
    if args.output_path:
        logger.warning("The --output-path option is deprecated, use --outfile instead.")
        outfile = args.output_path

    mnemonic = Mnemonic.generate()
    print(f"Mnemonic: {mnemonic.get_text()}")

    if format is None:
        return
    if outfile is None:
        raise Exception("The --outfile option is required when --format is specified.")

    outfile = Path(outfile).expanduser().resolve()
    if outfile.exists():
        raise Exception(f"File already exists, will not overwrite: {outfile}")

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
        raise Exception(f"Unknown format: {format}")

    logger.info(f"Wallet ({format}) saved: {outfile}")


def convert_wallet(args: Any):
    infile = Path(args.infile).expanduser().resolve()
    outfile = Path(args.outfile).expanduser().resolve()
    in_format = args.in_format
    out_format = args.out_format
    address_index = args.address_index
    address_hrp = args.address_hrp

    if outfile.exists():
        raise Exception(f"File already exists, will not overwrite: {outfile}")

    # Parse the input
    mnemonic: Optional[Mnemonic] = None
    secret_key: Optional[UserSecretKey] = None

    if in_format == WALLET_FORMAT_RAW_MNEMONIC:
        mnemonic = Mnemonic(infile.read_text())
    elif in_format == WALLET_FORMAT_KEYSTORE_MNEMONIC:
        password = getpass.getpass("Enter the password for the input keystore:")
        keyfile = json.loads(infile.read_text())
        mnemonic = UserWallet.decrypt_mnemonic(keyfile, password)
    elif in_format == WALLET_FORMAT_KEYSTORE_SECRET_KEY:
        password = getpass.getpass("Enter the password for the input keystore:")
        keyfile = json.loads(infile.read_text())
        secret_key = UserWallet.decrypt_secret_key(keyfile, password)
    elif in_format == WALLET_FORMAT_PEM:
        secret_key = UserPEM.from_file(infile, address_index).secret_key
    else:
        raise Exception(f"Unknown input format: {in_format}")

    # Convert and save
    if out_format == WALLET_FORMAT_RAW_MNEMONIC:
        if mnemonic is None:
            raise Exception(f"Cannot convert {in_format} to {out_format}.")

        outfile.write_text(mnemonic.get_text())
    elif out_format == WALLET_FORMAT_KEYSTORE_MNEMONIC:
        if mnemonic is None:
            raise Exception(f"Cannot convert {in_format} to {out_format}.")

        password = getpass.getpass("Enter a new password (for the output keystore):")
        wallet = UserWallet.from_mnemonic(mnemonic.get_text(), password)
        wallet.save(outfile)
    elif out_format == WALLET_FORMAT_KEYSTORE_SECRET_KEY:
        if mnemonic:
            secret_key = mnemonic.derive_key(address_index)
        assert secret_key is not None

        password = getpass.getpass("Enter a new password (for the output keystore):")
        wallet = UserWallet.from_secret_key(secret_key, password)
        wallet.save(outfile, address_hrp)
    elif out_format == WALLET_FORMAT_PEM:
        if mnemonic:
            secret_key = mnemonic.derive_key(address_index)
        assert secret_key is not None

        pubkey = secret_key.generate_public_key()
        address = pubkey.to_address(address_hrp)
        pem_file = UserPEM(address.bech32(), secret_key)
        pem_file.save(outfile)
    else:
        raise Exception(f"Unknown output format: {out_format}")

    logger.info(f"Wallet ({out_format}) saved: {outfile}")


def generate_pem(args: Any):
    logger.warning("This command is deprecated. Use 'wallet convert' instead.")

    pem_file_path = Path(args.pem)
    ask_mnemonic = args.mnemonic
    index = args.index

    if ask_mnemonic:
        mnemonic_str = input("Enter mnemonic:\n").rstrip().replace("\n", "")
        mnemonic = Mnemonic(mnemonic_str)
        secret_key = mnemonic.derive_key(index)
        pubkey = secret_key.generate_public_key()
    else:
        mnemonic = Mnemonic.generate()

    secret_key = mnemonic.derive_key(index)
    pubkey = secret_key.generate_public_key()
    address = Address(pubkey.hex())

    pem_file = UserPEM(address.bech32(), secret_key)
    pem_file.save(pem_file_path)

    logger.info(f"Created PEM file [{pem_file_path}] for [{address.bech32()}]")


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
