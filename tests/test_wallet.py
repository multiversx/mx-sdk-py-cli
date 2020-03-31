import logging
import unittest
from pathlib import Path

import nacl.encoding
import nacl.signing

from erdpy.wallet import signing
from erdpy.transactions import PlainTransaction, TransactionPayloadToSign

logging.basicConfig(level=logging.INFO)


class WalletTestCase(unittest.TestCase):
    def setUp(self):
        self.testdata = Path(__file__).parent.joinpath("testdata")

    def test_nacl_playground_signing(self):
        private_key_hex = "b8211b08edc8aca591bedf1b9aba47e4077e54ac7d4ceb2f1bc9e10c064d3e6c7a5679a427f6df7adf2310ddf5e570fd51e47e6b1511124d6b250b989b017588"
        private_key_bytes = bytes.fromhex(private_key_hex)
        private_key_seed_bytes = private_key_bytes[:32]
        signing_key = nacl.signing.SigningKey(private_key_seed_bytes)
        signed = signing_key.sign(b"test")
        signature = signed.signature
        signed_bytes_hex = signature.hex()

        self.assertEqual("a4918458d874ca58893a1f92dac33e7b10e3bf46048ad5de5bc260487ca84e8e07603297120fdc018242f63bd8e87b13efd108f8ffa095f536b6eda03805590c", signed_bytes_hex)
        self.assertEqual(64, len(signature))

    def test_get_address_from_pem(self):
        pem = self.testdata.joinpath("keys", "alice.pem")
        address = signing.get_address_from_pem(pem)
        self.assertEqual("93ee6143cdc10ce79f15b2a6c2ad38e9b6021c72a1779051f47154fd54cfbd5e", address.hex())

    def test_parse_pem(self):
        pem = self.testdata.joinpath("keys", "alice.pem")
        seed, address = signing.parse_pem(pem)

        self.assertEqual("aa137cb6a0022f18ea2d31f00025190fb09961deb624e18cf11f6e867ccb45d3", seed.hex())
        self.assertEqual("93ee6143cdc10ce79f15b2a6c2ad38e9b6021c72a1779051f47154fd54cfbd5e", address.hex())

    def test_sign_transaction(self):
        pem = self.testdata.joinpath("keys", "alice.pem")

        transaction = PlainTransaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "93ee6143cdc10ce79f15b2a6c2ad38e9b6021c72a1779051f47154fd54cfbd5e"
        transaction.receiver = "a967adb3d1574581a6f7ffe0cd6600fb488686704fcff944c88efc7c90b3b13b"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = ""
        payload = TransactionPayloadToSign(transaction)
        signature = signing.sign_transaction(payload, pem)

        self.assertEqual("04e98acb3c844bcf49fcd07417fdfe5edc9df4419f7deed49262145d3759f687c1cda202cda51808ad0834b472ccf1f5334b952e3cb1fd0b98721c6bfca10d04", signature)
