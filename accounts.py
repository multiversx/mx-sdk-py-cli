from erdpy.wallet import parse_pem


class Account:
    def __init__(self, address=None, pem_file=None):
        self.private_key_seed = None
        self.address = address

        if pem_file:
            seed, address = parse_pem(pem_file)
            self.private_key_seed = seed
            self.address = address

    def address_hex(self):
        return f"0x{self.address}"

    def address_bytes(self):
        pass

    def address_base64(self):
        pass
