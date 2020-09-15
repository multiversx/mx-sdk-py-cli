import hashlib
import hmac
import struct

import nacl.signing

BIP39_SALT_MODIFIER = "mnemonic"
BIP39_PBKDF2_ROUNDS = 2048
BIP32_SEED_MODIFIER = b'ed25519 seed'
ELROND_DERIVATION_PATH = [44, 508, 0, 0]
HARDENED_OFFSET = 0x80000000


def derive_keys(mnemonic, account_index=0):
    seed = mnemonic_to_bip39seed(mnemonic)
    private_key = bip39seed_to_private_key(seed, account_index)
    public_key = bytes(nacl.signing.SigningKey(private_key).verify_key)
    return private_key, public_key


# References:
# https://github.com/trezor/python-mnemonic/blob/master/mnemonic/mnemonic.py
# https://ethereum.stackexchange.com/a/72871/59887
def mnemonic_to_bip39seed(mnemonic, passphrase=""):
    passphrase = BIP39_SALT_MODIFIER + passphrase
    mnemonic = mnemonic.encode("utf-8")
    passphrase = passphrase.encode("utf-8")
    stretched = hashlib.pbkdf2_hmac("sha512", mnemonic, passphrase, BIP39_PBKDF2_ROUNDS)
    return stretched[:64]


# References:
# https://ethereum.stackexchange.com/a/72871/59887s
# https://github.com/alepop/ed25519-hd-key/blob/master/src/index.ts#L22
def bip39seed_to_master_key(seed):
    hashed = hmac.new(BIP32_SEED_MODIFIER, seed, hashlib.sha512).digest()
    key, chain_code = hashed[:32], hashed[32:]
    return key, chain_code


# Reference: https://github.com/alepop/ed25519-hd-key
def bip39seed_to_private_key(seed, account_index=0):
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
