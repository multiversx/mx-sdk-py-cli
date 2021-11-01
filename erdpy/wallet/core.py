import hashlib
import hmac
import secrets
import struct
from importlib.resources import open_text
from typing import List

import nacl.signing

BIP39_SALT_MODIFIER = "mnemonic"
BIP39_PBKDF2_ROUNDS = 2048
BIP32_SEED_MODIFIER = b'ed25519 seed'
ELROND_DERIVATION_PATH = [44, 508, 0, 0]
HARDENED_OFFSET = 0x80000000
BITS_PER_BYTE = 8
BIP39_WORD_COUNT = 2048
BIP39_ENTROPY_BITS = 256
BIP39_ENTROPY_BYTES = BIP39_ENTROPY_BITS // 8
BIP39_CHECKSUM_BITS = BIP39_ENTROPY_BITS // 32
BIP39_TOTAL_INDICES_BITS = BIP39_ENTROPY_BITS + BIP39_CHECKSUM_BITS
BIP39_WORD_BITS = 11
BIP39_MNEMONIC_WORD_COUNT = 24


def derive_keys(mnemonic, account_index=0):
    bip39seed = mnemonic_to_bip39seed(mnemonic)
    secret_key = bip39seed_to_secret_key(bip39seed, account_index)
    public_key = bytes(nacl.signing.SigningKey(secret_key).verify_key)
    return secret_key, public_key


# References:
# https://github.com/trezor/python-mnemonic/blob/master/mnemonic/mnemonic.py
# https://ethereum.stackexchange.com/a/72871/59887
def mnemonic_to_bip39seed(mnemonic, passphrase=""):
    passphrase = BIP39_SALT_MODIFIER + passphrase
    mnemonic = mnemonic.encode("utf-8")
    passphrase = passphrase.encode("utf-8")
    stretched = hashlib.pbkdf2_hmac("sha512", mnemonic, passphrase, BIP39_PBKDF2_ROUNDS)
    return stretched[:64]


def bytes_to_binary_string(bytes: bytes) -> str:
    number_of_bits = len(bytes) * BITS_PER_BYTE
    bytes_int = int.from_bytes(bytes, "big")
    return f"{bytes_int:0{number_of_bits}b}"


def split_to_fixed_size_slices(bits: str, chunk_size: int) -> List[str]:
    return [bits[i:i + chunk_size] for i in range(0, len(bits), chunk_size)]


def generate_mnemonic() -> str:
    entropy_bytes = secrets.token_bytes(BIP39_ENTROPY_BYTES)
    return generate_mnemonic_from_entropy(entropy_bytes)


# Word list from:
# https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt
# BIP39 algorithm steps from:
# https://medium.com/coinmonks/mnemonic-generation-bip39-simply-explained-e9ac18db9477
# Javascript implementations:
# https://github.com/ElrondNetwork/elrond-sdk-erdjs/blob/main/src/walletcore/mnemonic.ts
# https://github.com/bitcoinjs/bip39/blob/5faee2c17b2195f30b03cb125df68c20d7dd584b/src/index.js#L108
def generate_mnemonic_from_entropy(entropy_bytes: bytes) -> str:
    with open_text("erdpy.wallet", "bip39words.txt") as words_file:
        words = words_file.read().splitlines()
        assert len(words) == BIP39_WORD_COUNT

    assert len(entropy_bytes) == BIP39_ENTROPY_BYTES
    entropy_bits = bytes_to_binary_string(entropy_bytes)

    checksum_bytes = hashlib.sha256(entropy_bytes).digest()
    checksum_bits = bytes_to_binary_string(checksum_bytes)
    init_checksum_bits = checksum_bits[:BIP39_CHECKSUM_BITS]

    entropy_with_checksum_bits = entropy_bits + init_checksum_bits
    assert len(entropy_with_checksum_bits) == BIP39_TOTAL_INDICES_BITS

    indices_bits = split_to_fixed_size_slices(entropy_with_checksum_bits, BIP39_WORD_BITS)
    indices_ints = [int(index_bits, base=2) for index_bits in indices_bits]
    assert len(indices_ints) == BIP39_MNEMONIC_WORD_COUNT

    mnemonic_words = [words[word_index] for word_index in indices_ints]
    mnemonic = " ".join(mnemonic_words)
    return mnemonic


# References:
# https://ethereum.stackexchange.com/a/72871/59887s
# https://github.com/alepop/ed25519-hd-key/blob/master/src/index.ts#L22
def bip39seed_to_master_key(seed):
    hashed = hmac.new(BIP32_SEED_MODIFIER, seed, hashlib.sha512).digest()
    key, chain_code = hashed[:32], hashed[32:]
    return key, chain_code


# Reference: https://github.com/alepop/ed25519-hd-key
def bip39seed_to_secret_key(seed, account_index=0):
    key, chain_code = bip39seed_to_master_key(seed)

    for segment in ELROND_DERIVATION_PATH + [account_index]:
        key, chain_code = _ckd_priv(key, chain_code, segment + HARDENED_OFFSET)

    return key


# Reference: https://github.com/alepop/ed25519-hd-key
def _ckd_priv(key, chain_code, index):
    index_buffer = struct.pack('>I', index)
    data = bytearray([0]) + bytearray(key) + bytearray(index_buffer)
    hashed = hmac.new(chain_code, data, hashlib.sha512).digest()
    key, chain_code = hashed[:32], hashed[32:]

    return key, chain_code
