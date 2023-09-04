from getpass import getpass
from typing import Any


def load_password(args: Any) -> str:
    if args.passfile:
        with open(args.passfile) as pass_file:
            return pass_file.read().strip()
    return getpass("Keyfile's password: ")


def load_guardian_password(args: Any) -> str:
    if args.guardian_passfile:
        with open(args.guardian_passfile) as pass_file:
            return pass_file.read().strip()
    return getpass("Keyfile's password: ")
