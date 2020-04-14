import logging

from erdpy import errors
from erdpy.wallet import bech32, parse_pem

logger = logging.getLogger("accounts")


class Account:
    def __init__(self, address=None, pem_file=None):
        self.private_key_seed = None
        self.address = Address(address)
        self.pem_file = pem_file
        self.nonce = 0

        if pem_file:
            seed, pubkey = parse_pem(pem_file)
            self.private_key_seed = seed.hex()
            self.address = Address(pubkey)

    def sync_nonce(self, proxy):
        logger.info(f"Account.sync_nonce()")
        self.nonce = proxy.get_account_nonce(self.address)
        logger.info(f"Account.sync_nonce() done: {self.nonce}")


class Address:
    HRP = "erd"
    PUBKEY_LENGTH = 32
    PUBKEY_STRING_LENGTH = PUBKEY_LENGTH * 2    # hex-encoded
    BECH32_LENGTH = 62

    def __init__(self, value):
        self._value_hex = None

        if not value:
            return

        # Copy-constructor
        if isinstance(value, Address):
            value = value._value_hex

        # We keep a hex-encoded string as the "backing" value
        if len(value) == Address.PUBKEY_LENGTH:
            self._value_hex = value.hex()
        elif len(value) == Address.PUBKEY_STRING_LENGTH:
            self._value_hex = _as_string(value)
        elif len(value) == Address.BECH32_LENGTH:
            self._value_hex = _decode_bech32(value).hex()
        else:
            raise errors.BadAddressFormatError(value)

    def hex(self):
        self._assert_validity()
        return self._value_hex

    def bech32(self):
        self._assert_validity()
        pubkey = self.pubkey()
        return bech32.bech32_encode(self.HRP, bech32.convertbits(pubkey, 8, 5))

    def pubkey(self):
        self._assert_validity()
        pubkey = bytes.fromhex(self._value_hex)
        return pubkey

    def _assert_validity(self):
        if self._value_hex is None:
            raise errors.EmptyAddressError()

    @classmethod
    def zero(cls):
        return Address("0" * 64)


def _as_string(value):
    if isinstance(value, str):
        return value
    return value.decode("utf-8")


def _decode_bech32(value):
    bech32_string = _as_string(value)
    hrp, value_bytes = bech32.bech32_decode(bech32_string)
    if hrp != Address.HRP:
        raise errors.BadAddressFormatError(value)
    decodedBytes = bech32.convertbits(value_bytes, 5, 8, False)
    return bytearray(decodedBytes)
