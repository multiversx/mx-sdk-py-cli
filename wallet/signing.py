import logging
from typing import Any

import nacl.encoding
import nacl.signing

from erdpy import myprocess, workstation
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
    # sign message with a go binary
    try:
        path = workstation.get_tools_folder()
        path_to_mcl_signer = f'{path}/signer/signer'
        signed_message = myprocess.run_process([path_to_mcl_signer, message, seed], dump_to_stdout=False)
        return signed_message
    except Exception:
        raise CannotSignMessageWithBLSKey()
