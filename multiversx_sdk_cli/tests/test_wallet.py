import logging

import nacl.signing
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

    def test_nacl_playground_signing(self):
        secret_key_hex = "b8211b08edc8aca591bedf1b9aba47e4077e54ac7d4ceb2f1bc9e10c064d3e6c7a5679a427f6df7adf2310ddf5e570fd51e47e6b1511124d6b250b989b017588"
        secret_key_bytes = bytes.fromhex(secret_key_hex)
        secret_key_seed_bytes = secret_key_bytes[:32]
        signing_key = nacl.signing.SigningKey(secret_key_seed_bytes)
        signed = signing_key.sign(b"test")
        signature = signed.signature
        signed_bytes_hex = signature.hex()

        self.assertEqual(
            "a4918458d874ca58893a1f92dac33e7b10e3bf46048ad5de5bc260487ca84e8e07603297120fdc018242f63bd8e87b13efd108f8ffa095f536b6eda03805590c",
            signed_bytes_hex)
        self.assertEqual(64, len(signature))

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
