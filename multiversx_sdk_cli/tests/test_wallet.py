import logging

from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.errors import GasLimitTooLarge
from multiversx_sdk_cli.tests.utils import MyTestCase
from multiversx_sdk_cli.transactions import Transaction

logging.basicConfig(level=logging.INFO)


class WalletTestCase(MyTestCase):
    def setUp(self):
        super().setUp()
        self.alice = Account(pem_file=str(self.devnet_wallets.joinpath("users", "alice.pem")))
        self.multiple_bls_keys_file = self.testdata / 'multipleValidatorsKeys.pem'

    def test_sign_transaction(self):
        # With data
        transaction = Transaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = "foo"
        transaction.chainID = "chainID"
        transaction.version = 1
        transaction.sign(self.alice)

        self.assertEqual(
            "0e69f27e24aba2f3b7a8842dc7e7c085a0bfb5b29112b258318eed73de9c8809889756f8afaa74c7b3c7ce20a028b68ba90466a249aaf999a1a78dcf7f4eb40c",
            transaction.signature)

        # Without data
        transaction = Transaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = ""
        transaction.chainID = "chainID"
        transaction.version = 1
        transaction.sign(self.alice)

        self.assertEqual("83efd1bc35790ecc220b0ed6ddd1fcb44af6653dd74e37b3a49dcc1f002a1b98b6f79779192cca68bdfefd037bc81f4fa606628b751023122191f8c062362805", transaction.signature)

    def test_gas_limit_too_large(self):
        # With data
        transaction = Transaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 1500000000
        transaction.data = "foo"
        transaction.chainID = "chainID"
        transaction.version = 1

        self.assertRaises(GasLimitTooLarge, lambda: transaction.sign(self.alice))
