import logging
from erdpy.wallet import parse_pem


logger = logging.getLogger("accounts")


class Account:
    def __init__(self, address=None, pem_file=None):
        self.private_key_seed = None
        self.address = address
        self.pem_file = pem_file
        self.nonce = 0

        if pem_file:
            seed, address = parse_pem(pem_file)
            self.private_key_seed = seed.hex()
            self.address = address.hex()

    def address_formatted(self):
        return f"0x{self.address}"

    def address_hex(self):
        return self.address

    def address_bytes(self):
        return bytearray.fromhex(self.address)

    def address_base64(self):
        pass

    def sync_nonce(self, proxy):
        logger.info(f"Account.sync_nonce()")
        self.nonce = proxy.get_account_nonce(self.address)
        logger.info(f"Account.sync_nonce() done: {self.nonce}")
