import shutil
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Tuple

from multiversx_sdk_cli import errors, utils
from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.wallet import pem
from multiversx_sdk_cli.workstation import get_tools_folder

MAX_NUM_NODES = 12


def copy_all_to(destination: str):
    shutil.copytree(_get_folder(), destination)


def copy_validator_key_to(validator_index: int, destination: str):
    shutil.copy(get_validator_key_file(validator_index), destination)


def get_validator_key_file(validator_index: int):
    _guard_validator_index(validator_index)
    return _get_validators_folder().joinpath("validatorKey{:02}.pem".format(validator_index))


def get_observer_key_file(observer_index: int):
    _guard_validator_index(observer_index)
    return _get_observers_folder().joinpath("observerKey{:02}.pem".format(observer_index))


def get_validator_wallets(num_validators: int) -> Dict[str, Account]:
    result = {}

    for i in range(0, num_validators):
        pem_file = get_validator_wallet_file(i)
        nickname = "validator{:02}".format(i)
        account = Account(pem_file=pem_file)
        result[nickname] = account

    return result


def get_validators(num_validators: int) -> Dict[str, Tuple[str, Account]]:
    result = {}

    for i in range(0, num_validators):
        validator_pem_file = get_validator_key_file(i)
        _, pubkey = pem.parse_validator_pem(validator_pem_file)

        pem_file = get_validator_wallet_file(i)
        nickname = "validator{:02}".format(i)
        account = Account(pem_file=pem_file)
        result[nickname] = (pubkey, account)

    return result


def get_validator_wallet_file(validator_index: int):
    _guard_validator_index(validator_index)
    return _get_validators_folder().joinpath("wallet{:02}.pem".format(validator_index))


def _guard_validator_index(validator_index: int):
    if validator_index >= MAX_NUM_NODES:
        raise errors.TestnetError(f"Invalid validator index: {validator_index} >= {MAX_NUM_NODES}.")


def _get_validators_folder():
    return _get_folder().joinpath("validators")


def _get_observers_folder():
    return _get_folder().joinpath("observers")


def get_users() -> Dict[str, Account]:
    result: Dict[str, Account] = OrderedDict()

    for pem_file in sorted(utils.list_files(_get_users_folder(), ".pem")):
        nickname = Path(pem_file).stem
        account = Account(pem_file=str(pem_file))
        result[nickname] = account

    return result


def _get_users_folder():
    return _get_folder().joinpath("users")


def _get_folder():
    return get_tools_folder() / "testwallets" / "latest" 
