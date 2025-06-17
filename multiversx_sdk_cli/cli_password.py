import logging
from getpass import getpass
from typing import Any

logger = logging.getLogger("cli.password")


def load_password(args: Any) -> str:
    if args.passfile:
        logger.warning(
            "Using a password file is deprecated and will be removed in a future version. You'll be prompted to enter the password when using keystore wallets."
        )
        with open(args.passfile) as pass_file:
            return pass_file.read().strip()
    return getpass("Keyfile's password: ")


def load_guardian_password(args: Any) -> str:
    if args.guardian_passfile:
        logger.warning(
            "Using a password file is deprecated and will be removed in a future version. You'll be prompted to enter the password when using keystore wallets."
        )
        with open(args.guardian_passfile) as pass_file:
            return pass_file.read().strip()
    return getpass("Keyfile's password: ")


def load_relayer_password(args: Any) -> str:
    if args.relayer_passfile:
        logger.warning(
            "Using a password file is deprecated and will be removed in a future version. You'll be prompted to enter the password when using keystore wallets."
        )
        with open(args.relayer_passfile) as pass_file:
            return pass_file.read().strip()
    return getpass("Keyfile's password: ")
