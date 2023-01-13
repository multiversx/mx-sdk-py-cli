import logging
import unittest
from pathlib import Path
from multiversx_sdk_cli import errors

from multiversx_sdk_cli.accounts import Address

logging.basicConfig(level=logging.INFO)


class AccountsTestCase(unittest.TestCase):
    def setUp(self):
        self.testdata = Path(__file__).parent.joinpath("testdata")

    def test_address(self):
        address = Address("erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz")
        address_cloned = Address(address)
        self.assertEqual("fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293", address.hex())
        self.assertEqual("erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz", address.bech32())
        self.assertEqual(address.hex(), address_cloned.hex())
        self.assertEqual(address.bech32(), address_cloned.bech32())

        address = Address("fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293")
        address_cloned = Address(address)
        self.assertEqual("fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293", address.hex())
        self.assertEqual("erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz", address.bech32())
        self.assertEqual(address.hex(), address_cloned.hex())
        self.assertEqual(address.bech32(), address_cloned.bech32())

        address = Address("")
        self.assertRaises(errors.EmptyAddressError, address.hex)
        self.assertRaises(errors.EmptyAddressError, address.bech32)

        address = Address(None)
        self.assertRaises(errors.EmptyAddressError, address.hex)
        self.assertRaises(errors.EmptyAddressError, address.bech32)

        with self.assertRaises(errors.BadAddressFormatError) as _:
            address = Address("bad")
