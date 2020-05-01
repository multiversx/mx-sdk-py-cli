import logging
import nacl.encoding
import nacl.signing

from erdpy.wallet import pem

logger = logging.getLogger("wallet")


def sign_transaction(transaction, pem_file):
    seed, _ = pem.parse(pem_file)
    signing_key = nacl.signing.SigningKey(seed)

    data_json = transaction.to_json()
    signed = signing_key.sign(data_json)
    signature = signed.signature
    signature_hex = signature.hex()

    return signature_hex
