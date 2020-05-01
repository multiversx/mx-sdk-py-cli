import base64
from os import path

from erdpy import utils, guards


def get_pubkey(pem_file):
    _, pubkey = parse(pem_file)
    return pubkey


def parse(pem_file):
    pem_file = path.expanduser(pem_file)
    guards.is_file(pem_file)

    lines = utils.read_lines(pem_file)
    lines = [line for line in lines if "-----" not in line]
    key_base64 = "".join(lines)
    key_hex = base64.b64decode(key_base64).decode()
    key_bytes = bytes.fromhex(key_hex)

    seed = key_bytes[:32]
    pubkey = key_bytes[32:]
    return seed, pubkey


def write(pem_file, seed, pubkey):
    combined = seed + pubkey
    key_base64 = base64.b64encode(combined).encode()
    utils.write_file(pem_file, key_base64)
