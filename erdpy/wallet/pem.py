import base64
import itertools
import textwrap
from os import path
from pathlib import Path
from typing import List, Tuple, Union

from erdpy import guards, utils


def get_pubkey(pem_file: Union[str, Path]):
    _, pubkey = parse(pem_file)
    return pubkey


def parse(pem_file: Union[str, Path], index: int = 0) -> Tuple[bytes, bytes]:
    pem_file = path.expanduser(pem_file)
    guards.is_file(pem_file)

    lines = utils.read_lines(pem_file)
    keys_lines = [list(key_lines) for is_next_key, key_lines in itertools.groupby(lines, lambda line: "-----" in line)
                  if not is_next_key]
    keys = ["".join(key_lines) for key_lines in keys_lines]

    key_base64 = keys[index]
    key_hex = base64.b64decode(key_base64).decode()
    key_bytes = bytes.fromhex(key_hex)

    seed = key_bytes[:32]
    pubkey = key_bytes[32:]
    return seed, pubkey


def parse_all(pem_file: Union[str, Path]) -> List[Tuple[bytes, bytes]]:
    pem_file = path.expanduser(pem_file)
    guards.is_file(pem_file)

    lines = utils.read_lines(pem_file)
    keys_lines = [list(key_lines) for is_next_key, key_lines in itertools.groupby(lines, lambda line: "-----" in line)
                  if not is_next_key]
    keys = ["".join(key_lines) for key_lines in keys_lines]

    result = []

    for key_base64 in keys:
        key_hex = base64.b64decode(key_base64).decode()
        key_bytes = bytes.fromhex(key_hex)
        seed = key_bytes[:32]
        pubkey = key_bytes[32:]

        result.append((seed, pubkey))

    return result


def parse_validator_pem(pem_file, index: int = 0):
    pem_file = path.expanduser(pem_file)
    guards.is_file(pem_file)

    lines = utils.read_lines(pem_file)
    bls_keys = read_bls_keys(lines)
    private_keys = read_validators_private_keys(lines)

    private_key = private_keys[index]
    key_bytes = get_bytes_from_private_key(private_key)

    bls_key = bls_keys[index]
    seed = key_bytes
    return seed, bls_key


def read_bls_keys(lines):
    bls_keys = []

    for line in lines:
        splited_line = line.split(" ")
        if len(splited_line) < 5:
            continue
        if "BEGIN" in splited_line[0]:
            continue

        token = splited_line[4].replace('-----', '')
        bls_keys.append(token)

    return bls_keys


def read_validators_private_keys(lines):
    private_keys = []

    private_keys_lines = [list(key_lines) for is_next_key, key_lines in
                          itertools.groupby(lines, lambda line: "-----" in line) if not is_next_key]
    for key_list in private_keys_lines:
        private_keys.append(key_list[0] + key_list[1])

    return private_keys


def get_bytes_from_private_key(private_key):
    key_base64 = private_key
    key_hex = base64.b64decode(key_base64).hex()
    key_bytes = bytes.fromhex(key_hex)

    return key_bytes


def write(pem_file: Union[str, Path], seed: bytes, pubkey: bytes, name: str = ""):
    pem_file = path.expanduser(pem_file)

    if not name:
        name = pubkey.hex()

    header = f"-----BEGIN PRIVATE KEY for {name}-----"
    footer = f"-----END PRIVATE KEY for {name}-----"

    seed_hex = seed.hex()
    pubkey_hex = pubkey.hex()
    combined = seed_hex + pubkey_hex
    combined_bytes = combined.encode()
    key_base64 = base64.b64encode(combined_bytes).decode()

    payload_lines = textwrap.wrap(key_base64, 64)
    payload = "\n".join(payload_lines)
    content = "\n".join([header, payload, footer])
    utils.write_file(pem_file, content)
