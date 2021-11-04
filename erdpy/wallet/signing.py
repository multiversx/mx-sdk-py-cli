import logging
from os import path
from typing import Any

import nacl.encoding
import nacl.signing
from erdpy import config, dependencies, myprocess
from erdpy import errors
from erdpy.errors import CannotSignMessageWithBLSKey
from erdpy.interfaces import IAccount, ITransaction
from erdpy.transactions import Transaction

logger = logging.getLogger("wallet")


def sign_transaction(transaction: ITransaction, account: IAccount) -> str:
    secret_key: bytes = account.get_secret_key()
    signing_key: Any = nacl.signing.SigningKey(secret_key)

    data_json = transaction.serialize()
    signed = signing_key.sign(data_json)
    signature = signed.signature
    signature_hex = signature.hex()
    assert isinstance(signature_hex, str)

    return signature_hex


def validate_transaction(transaction: Transaction) -> None:
    if transaction.gasLimit > config.MAX_GAS_LIMIT:
        raise errors.GasLimitTooLarge(transaction.gasLimit, config.MAX_GAS_LIMIT)


def sign_message_with_bls_key(message, seed):
    dependencies.install_module("mcl_signer")
    tool = path.join(dependencies.get_module_directory("mcl_signer"), "signer")

    try:
        signed_message = myprocess.run_process([tool, message, seed], dump_to_stdout=False)
        return signed_message
    except Exception:
        raise CannotSignMessageWithBLSKey()


def sign_message(message: bytes, account: IAccount) -> str:
    secret_key: bytes = account.get_secret_key()
    signing_key: Any = nacl.signing.SigningKey(secret_key)

    signed = signing_key.sign(message)
    signature = signed.signature
    signature_hex = signature.hex()
    assert isinstance(signature_hex, str)

    return signature_hex
