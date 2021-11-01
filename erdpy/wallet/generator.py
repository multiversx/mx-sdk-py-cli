import logging
import nacl.encoding
import nacl.signing

logger = logging.getLogger("wallet.generator")


def generate_pairs():
    pass


def generate_pair():
    signing_key = nacl.signing.SigningKey.generate()
    secret_key = bytes(signing_key)
    pubkey_bytes = bytes(signing_key.verify_key)
    return secret_key, pubkey_bytes
