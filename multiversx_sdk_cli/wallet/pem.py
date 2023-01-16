import base64
import itertools
import textwrap
from pathlib import Path
from typing import List, Tuple

from multiversx_sdk_cli import guards, utils


def get_pubkey(pem_file: Path):
    _, pubkey = parse(pem_file)
    return pubkey


def parse(pem_file: Path, index: int = 0) -> Tuple[bytes, bytes]:
    pem_file = pem_file.expanduser()
    guards.is_file(pem_file)

    lines = utils.read_lines(pem_file)
    keys_lines = [list(key_lines) for is_next_key, key_lines in itertools.groupby(lines, lambda line: "-----" in line)
                  if not is_next_key]
    keys = ["".join(key_lines) for key_lines in keys_lines]

    key_base64 = keys[index]
    key_hex = base64.b64decode(key_base64).decode()
    key_bytes = bytes.fromhex(key_hex)

    secret_key = key_bytes[:32]
    pubkey = key_bytes[32:]
    return secret_key, pubkey


def parse_all(pem_file: Path) -> List[Tuple[bytes, bytes]]:
    pem_file = pem_file.expanduser()
    guards.is_file(pem_file)

    lines = utils.read_lines(pem_file)
    keys_lines = [list(key_lines) for is_next_key, key_lines in itertools.groupby(lines, lambda line: "-----" in line)
                  if not is_next_key]
    keys = ["".join(key_lines) for key_lines in keys_lines]

    result = []

    for key_base64 in keys:
        key_hex = base64.b64decode(key_base64).decode()
        key_bytes = bytes.fromhex(key_hex)
        secret_key = key_bytes[:32]
        pubkey = key_bytes[32:]

        result.append((secret_key, pubkey))

    return result


def parse_validator_pem(pem_file: Path, index: int = 0):
    pem_file = pem_file.expanduser()
    guards.is_file(pem_file)

    lines = utils.read_lines(pem_file)
    bls_keys = read_bls_keys(lines)
    secret_keys = read_validators_secret_keys(lines)

    secret_key = secret_keys[index]
    secret_key_bytes = get_bytes_from_secret_key(secret_key)

    bls_key = bls_keys[index]
    return secret_key_bytes, bls_key


def read_bls_keys(lines) -> List[str]:
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


# TODO rewrite using generators or simplify the list comprehension within
def read_validators_secret_keys(lines):
    secret_keys = []

    secret_keys_lines = [list(key_lines) for is_next_key, key_lines in
                         itertools.groupby(lines, lambda line: "-----" in line) if not is_next_key]
    for key_list in secret_keys_lines:
        secret_keys.append(key_list[0] + key_list[1])

    return secret_keys


def get_bytes_from_secret_key(secret_key):
    key_base64 = secret_key
    key_hex = base64.b64decode(key_base64).hex()
    key_bytes = bytes.fromhex(key_hex)

    return key_bytes


def write(pem_file: Path, secret_key: bytes, pubkey: bytes, name: str = ""):
    pem_file = pem_file.expanduser()

    if not name:
        name = pubkey.hex()

    header = f"-----BEGIN PRIVATE KEY for {name}-----"
    footer = f"-----END PRIVATE KEY for {name}-----"

    secret_key_hex = secret_key.hex()
    pubkey_hex = pubkey.hex()
    combined = secret_key_hex + pubkey_hex
    combined_bytes = combined.encode()
    key_base64 = base64.b64encode(combined_bytes).decode()

    payload_lines = textwrap.wrap(key_base64, 64)
    payload = "\n".join(payload_lines)
    content = "\n".join([header, payload, footer])
    utils.write_file(pem_file, content)
