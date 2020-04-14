import logging
import nacl.encoding
import nacl.signing
import base64
from os import path

from erdpy import utils, guards
from erdpy.wallet import bech32

logger = logging.getLogger("wallet")


def get_address_from_pem(pem_file):
    _, address = parse_pem(pem_file)
    return address


def sign_transaction(transaction, pem_file):
    seed, address = parse_pem(pem_file)
    signing_key = nacl.signing.SigningKey(seed)

    data_json = transaction.to_json()
    signed = signing_key.sign(data_json)
    signature = signed.signature
    signature_hex = signature.hex()

    return signature_hex


def parse_pem(pem_file):
    pem_file = path.expanduser(pem_file)
    guards.is_file(pem_file)

    lines = utils.read_lines(pem_file)
    lines = [line for line in lines if "-----" not in line]
    key_base64 = "".join(lines)
    key_hex = base64.b64decode(key_base64).decode()
    key_bytes = bytes.fromhex(key_hex)

    seed = key_bytes[:32]
    address = key_bytes[32:]
    address = bech32.bech32_encode("erd", bech32.convertbits(address, 8, 5))
    logger.info(f"Loaded PEM file for address [{address}]")

    return seed, address


def generate_account():
    pass
