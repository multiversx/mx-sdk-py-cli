from typing import Any
from getpass import getpass


def load_password(args: Any):
    if args.passfile:
        with open(args.passfile) as pass_file:
            return pass_file.read().strip()
    return getpass("Keyfile's password: ")


def load_guardian_password(args: Any):
    if args.guardian_passfile:
        with open(args.guardian_passfile) as pass_file:
            return pass_file.read().strip()
    return getpass("Keyfile's password: ")
