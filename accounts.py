from os import path
from erdpy import utils


class Account:
    def __init__(self, address, pem_file=None):
        pem_file = path.expanduser(pem_file)

        self.address = address
        self.pem = utils.read_file(pem_file) if pem_file is not None else None
