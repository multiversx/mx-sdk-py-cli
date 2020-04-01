import logging
import unittest
from pathlib import Path

from Crypto.Hash import keccak
from erdpy.accounts import Account
from erdpy.contracts import SmartContract

logging.basicConfig(level=logging.INFO)


class ContractsTestCase(unittest.TestCase):
    def setUp(self):
        self.testdata = Path(__file__).parent.joinpath("testdata")

    def test_playground_keccak(self):
        hash = keccak.new(digest_bits=256).update(b"").hexdigest()
        self.assertEqual("c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470", hash)

    def test_compute_address(self):
        contract = SmartContract()
        contract.owner = Account("93ee6143cdc10ce79f15b2a6c2ad38e9b6021c72a1779051f47154fd54cfbd5e")

        contract.owner.nonce = 0
        contract.compute_address()
        self.assertEqual("00000000000000000500bb652200ed1f994200ab6699462cab4b1af7b11ebd5e", contract.address)

        contract.owner.nonce = 1
        contract.compute_address()
        self.assertEqual("000000000000000005006e4f90488e27342f9a46e1809452c85ee7186566bd5e", contract.address)
