import logging
import unittest
from pathlib import Path

from erdpy.contracts import SmartContract
from erdpy.accounts import Account

logging.basicConfig(level=logging.INFO)


class ContractsTestCase(unittest.TestCase):
    def setUp(self):
        self.testdata = Path(__file__).parent.joinpath("testdata")

    def test_compute_address(self):
        contract = SmartContract()
        contract.owner = Account("93ee6143cdc10ce79f15b2a6c2ad38e9b6021c72a1779051f47154fd54cfbd5e")

        contract.owner.nonce = 0
        contract.compute_address()
        self.assertEqual("000000000000000000052c53ff3ac9360413569c3e12a68e577736241ac4bd5e", contract.address)

        contract.owner.nonce = 1
        contract.compute_address()
        self.assertEqual("00000000000000000005981e67c1cc99f4c7473ec53f2421c830ff95273dbd5e", contract.address)
