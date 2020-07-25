import logging
from pathlib import Path
from typing import Any, Union
import nacl.encoding
import nacl.signing

from erdpy import myprocess, workstation
from erdpy.errors import CannotSignMessageWithBLSKey
from erdpy.wallet import pem

logger = logging.getLogger("wallet")


def sign_transaction(transaction: Any, pem_file: Union[str, Path]) -> str:
    seed, _ = pem.parse(pem_file)
    return sign_tx(transaction, seed)


def sign_transaction_with_seed(transaction: Any, seed: bytes) -> str:
    return sign_tx(transaction, seed)


def sign_tx(transaction: Any, seed: bytes) -> str:
    signing_key: Any = nacl.signing.SigningKey(seed)

    data_json = transaction.serialize_for_signing()
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
