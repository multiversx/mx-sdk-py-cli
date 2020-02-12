from os import path
from erdpy import utils


class Account:
    def __init__(self, address, pem_file=None):
        self.address = address
        self.pem = None

        if pem_file:
            pem_file = path.expanduser(pem_file)
            self.pem = utils.read_file(pem_file)
