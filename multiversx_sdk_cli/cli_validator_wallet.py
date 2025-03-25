import logging
from pathlib import Path
from typing import Any

from multiversx_sdk import ValidatorPEM, ValidatorSecretKey, ValidatorSigner

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.errors import BadUserInput
from multiversx_sdk_cli.sign_verify import SignedMessage, sign_message_by_validator
from multiversx_sdk_cli.ux import show_critical_error, show_message

logger = logging.getLogger("cli.validator_wallet")


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers,
        "validator-wallet",
        "Create a validator wallet, sign and verify messages and convert a validator wallet to a hex secret key.",
    )
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(
        subparsers,
        "validator-wallet",
        "new",
        "Create a new validator wallet and save it as a PEM file.",
    )
    sub.add_argument(
        "--outfile",
        help="the output path and file name for the generated wallet",
        type=str,
        required=True,
    )
    sub.set_defaults(func=create_new_wallet)

    sub = cli_shared.add_command_subparser(subparsers, "validator-wallet", "sign-message", "Sign a message.")
    sub.add_argument("--message", required=True, help="the message you want to sign")
    sub.add_argument("--pem", required=True, type=str, help="the path to a validator pem file")
    sub.add_argument(
        "--index",
        required=False,
        type=int,
        default=0,
        help="the index of the validator in case the file contains multiple validators (default: %(default)s)",
    )
    sub.set_defaults(func=sign_message)

    sub = cli_shared.add_command_subparser(
        subparsers, "validator-wallet", "verify-message-signature", "Verify a previously signed message."
    )
    sub.add_argument("--pubkey", required=True, help="the hex string representing the validator's public key")
    sub.add_argument(
        "--message",
        required=True,
        help="the previously signed message(readable text, as it was signed)",
    )
    sub.add_argument("--signature", required=True, help="the signature in hex format")
    sub.set_defaults(func=verify_message_signature)

    sub = cli_shared.add_command_subparser(
        subparsers, "validator-wallet", "convert", "Convert a validator pem file to a hex secret key."
    )
    sub.add_argument("--infile", required=True, help="the pem file of the wallet")
    sub.add_argument(
        "--index",
        required=False,
        type=int,
        default=0,
        help="the index of the validator in case the file contains multiple validators (default: %(default)s)",
    )
    sub.set_defaults(func=convert_wallet_to_secret_key)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def create_new_wallet(args: Any):
    path = Path(args.outfile).expanduser().resolve()

    if path.exists():
        raise BadUserInput(f"File already exists, will not overwrite: {str(path)}")

    secret_key = ValidatorSecretKey.generate()
    public_key = secret_key.generate_public_key()
    validator_pem = ValidatorPEM(label=public_key.hex(), secret_key=secret_key)
    validator_pem.save(path)

    logger.info(f"Validator wallet saved: {str(path)}")


def sign_message(args: Any):
    path = Path(args.pem).expanduser().resolve()
    validator_signer = ValidatorSigner.from_pem_file(path, args.index)
    signed_message = sign_message_by_validator(args.message, validator_signer)

    utils.dump_out_json(signed_message.to_dictionary())


def verify_message_signature(args: Any):
    message = args.message
    pubkey = args.pubkey

    signed_message = SignedMessage(pubkey, message, args.signature)
    is_signed = signed_message.verify_validator_signature()

    if is_signed:
        show_message(f"""SUCCESS: The message "{message}" was signed by {pubkey}""")
    else:
        show_critical_error(f"""FAILED: The message "{message}" was NOT signed by {pubkey}""")


def convert_wallet_to_secret_key(args: Any):
    file = args.infile
    index = args.index

    path = Path(file).expanduser().resolve()
    if not path.is_file():
        raise BadUserInput("File not found")

    signer = ValidatorSigner.from_pem_file(path, index)
    print(f"Public key: {signer.get_pubkey().hex()}")
    print(f"Secret key: {signer.secret_key.hex()}")
