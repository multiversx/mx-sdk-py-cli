import logging
import unittest
from pathlib import Path

import nacl.encoding
import nacl.signing
from erdpy import utils
from erdpy.transactions import PlainTransaction, TransactionPayloadToSign
from erdpy.wallet import generate_pair, pem, signing

logging.basicConfig(level=logging.INFO)


class WalletTestCase(unittest.TestCase):
    def setUp(self):
        self.testdata = Path(__file__).parent.joinpath("testdata")
        self.testdata_out = Path(__file__).parent.joinpath("testdata-out")
        utils.ensure_folder(self.testdata_out)

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

    def test_pem_get_pubkey(self):
        pem_file = self.testdata.joinpath("keys", "alice.pem")
        address = pem.get_pubkey(pem_file)

        self.assertEqual("fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293", address.hex())

    def test_pem_parse(self):
        pem_file = self.testdata.joinpath("keys", "alice.pem")
        seed, address = pem.parse(pem_file)

        self.assertEqual("1a927e2af5306a9bb2ea777f73e06ecc0ac9aaa72fb4ea3fecf659451394cccf", seed.hex())
        self.assertEqual("fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293", address.hex())

    def test_serialize_transaction_payload(self):
        # With data field
        transaction = PlainTransaction()
        transaction.nonce = 0
        transaction.value = "42"
        transaction.sender = "alice"
        transaction.receiver = "bob"
        transaction.gasPrice = 43
        transaction.gasLimit = 44
        transaction.data = "foobar"
        serialized = TransactionPayloadToSign(transaction).to_json().decode()
        self.assertEqual("""{"nonce":0,"value":"42","receiver":"bob","sender":"alice","gasPrice":43,"gasLimit":44,"data":"foobar"}""", serialized)

        # Without data field
        transaction.data = ""
        serialized = TransactionPayloadToSign(transaction).to_json().decode()
        self.assertEqual("""{"nonce":0,"value":"42","receiver":"bob","sender":"alice","gasPrice":43,"gasLimit":44}""", serialized)

        # With actual addresses
        transaction = PlainTransaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = "foo"
        serialized = TransactionPayloadToSign(transaction).to_json().decode()
        self.assertEqual("""{"nonce":0,"value":"0","receiver":"erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr","sender":"erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz","gasPrice":200000000000000,"gasLimit":500000000,"data":"foo"}""", serialized)

    def test_sign_transaction(self):
        pem = self.testdata.joinpath("keys", "alice.pem")

        # With data
        transaction = PlainTransaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = "foo"
        payload = TransactionPayloadToSign(transaction)
        signature = signing.sign_transaction(payload, pem)

        self.assertEqual("8e68002bdd45d04508b7325d1cab9195680acf03a4cd5cba23629a85074bf92a88275f1f2bc3c2bd19d8f5cd62bde83186d86932b04e0f5b88a374a824547009", signature)

        # Without data
        transaction = PlainTransaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = ""
        payload = TransactionPayloadToSign(transaction)
        signature = signing.sign_transaction(payload, pem)

        self.assertEqual("4e160bcafb6cb8ab8fc3260d3faf24bf7ce1205b5685adb457803db6d67c648a614308d8354e40b40fbb90c227046d6997493f798b92acb1b4bc49173939e703", signature)

    def test_generate_pair_pem(self):
        seed, pubkey = generate_pair()
        pem_file = Path(self.testdata_out, "foo.pem")
        pem.write(pem_file, seed, pubkey)
        parsed_seed, parsed_pubkey = pem.parse(pem_file)

        self.assertEqual(seed, parsed_seed)
        self.assertEqual(pubkey, parsed_pubkey)
