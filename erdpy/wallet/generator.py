import logging
import nacl.encoding
import nacl.signing
import base64
from os import path

from erdpy import utils, guards

logger = logging.getLogger("wallet.generator")


def generate_pairs():
    pass


def generate_pair():
    signing_key = nacl.signing.SigningKey.generate()
    seed_bytes = bytes(signing_key)
    pubkey_bytes = bytes(signing_key.verify_key)
    return seed_bytes, pubkey_bytes
