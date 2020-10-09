import logging
from os import path
from typing import Any

import nacl.encoding
import nacl.signing
from erdpy import dependencies, myprocess
from erdpy.errors import CannotSignMessageWithBLSKey
from erdpy.interfaces import IAccount, ITransaction

logger = logging.getLogger("wallet")


def sign_transaction(transaction: ITransaction, account: IAccount) -> str:
    seed: bytes = account.get_seed()
    signing_key: Any = nacl.signing.SigningKey(seed)

    data_json = transaction.serialize()
    signed = signing_key.sign(data_json)
    signature = signed.signature
    signature_hex = signature.hex()

    return signature_hex


def sign_message_with_bls_key(message, seed):
    dependencies.install_module("mcl_signer")
    tool = path.join(dependencies.get_module_directory("mcl_signer"), "signer")

    try:
        signed_message = myprocess.run_process([tool, message, seed], dump_to_stdout=False)
        return signed_message
    except Exception:
        raise CannotSignMessageWithBLSKey()
