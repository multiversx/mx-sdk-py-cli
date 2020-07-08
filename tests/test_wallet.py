import logging
import unittest
from pathlib import Path

import nacl.encoding
import nacl.signing

from erdpy import config, utils
from erdpy.transactions import PlainTransaction, TransactionPayloadToSign
from erdpy.wallet import generate_pair, mnemonic_to_bip39seed, pem, signing, bip39seed_to_private_key

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

    def test_sign_transaction_with_chain_and_version(self):
        config.get_with_chain_and_version = lambda: True

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
        transaction.chainID = "chainID"
        transaction.version = 1
        payload = TransactionPayloadToSign(transaction)
        signature = signing.sign_transaction(payload, pem)

        self.assertEqual("be94075c4cf472abfcbe38c08d96c21e85c95ea69d8845d6414b6c30d1226486c55452f6068fd1835d64eb5d67ef6c3f8025123984893754f03958bd8aa59407", signature)

        # Without data
        transaction = PlainTransaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = ""
        transaction.chainID = "chainID"
        transaction.version = 1
        payload = TransactionPayloadToSign(transaction)
        signature = signing.sign_transaction(payload, pem)

        self.assertEqual("1ad14993a3cf6a5e0898a29271a2924fc34f80ba2a391dd2ff5c2fcc554e5a71eda0e34044f99888ec1a1da6d4cf82345e848cec69ccd27e192f8b66c4beaa0c", signature)    

    def test_sign_transaction_trust_wallet_scenario(self):
        pem = self.testdata.joinpath("keys", "alice.pem")

        # With data
        transaction = PlainTransaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = "foo"
        payload = TransactionPayloadToSign(transaction)
        signature = signing.sign_transaction(payload, pem)

        self.assertEqual("3c807eddeb5c9d7864ca3a97da8d2bffcef84826228567d4c7478812fdd09858f438a5cade3341bb2b02a2a8717d271b9163735d65f61795f5dd946f519fc500", signature)

        # Without data
        transaction = PlainTransaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = ""
        payload = TransactionPayloadToSign(transaction)
        signature = signing.sign_transaction(payload, pem)

        self.assertEqual("39ab0e18bfce04bf53c9610faa3b9e7cecfca919510a7631e529e9086279b70a4832df32a5d1b8fdceb4e9082f2995da97f9195532c8d611ee749bc312cbf90c", signature)

    def test_sign_transaction_trust_wallet_scenario_with_chain_and_version(self):
        config.get_with_chain_and_version = lambda: True

        pem = self.testdata.joinpath("keys", "alice.pem")

        # With data
        transaction = PlainTransaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = "foo"
        transaction.chainID = "m1.0"
        transaction.version = 1
        payload = TransactionPayloadToSign(transaction)
        signature = signing.sign_transaction(payload, pem)

        self.assertEqual("fd77f627294c2cad3c4b0c761cad70e886fa1cfd119803caa2bcbc2d5ed3518df3e7531de9daa8ab47b278ac97a0cca5797868bdaba759845ce8c2c91162c30f", signature)

        # Without data
        transaction = PlainTransaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = ""
        transaction.chainID = "m1.0"
        transaction.version = 1
        payload = TransactionPayloadToSign(transaction)
        signature = signing.sign_transaction(payload, pem)

        self.assertEqual("c621788d31825a9ff5f6719e0677a734986c34aa2d1ea1c932854180898c6b8e970570c42c7880818efa37cc233499225bd45783008551a5b16ce12a54cc6506", signature)

    def test_generate_pair_pem(self):
        seed, pubkey = generate_pair()
        pem_file = Path(self.testdata_out, "foo.pem")
        pem.write(pem_file, seed, pubkey)
        parsed_seed, parsed_pubkey = pem.parse(pem_file)

        self.assertEqual(seed, parsed_seed)
        self.assertEqual(pubkey, parsed_pubkey)

    def test_derive_private_key(self):
        # password = "Password1!"
        # keystore_file = "erd1zzhmdm2uwv9l7d2ak72c4cv6gek5c797s7qdkfc3jthvrvnxc2jqdsnp9y.json"
        mnemonic = "emotion spare multiply lecture rude machine raise radio ability doll depend equip pass ghost cabin delay birth opera shoe force any slow fluid old"
        mnemonic_seed = "2c3afb9202816c0ad8cfffbfe60b086c3b0600e7e96eddb589ca6bfcb2826a073c823b1c73200f152bd768c47754d7bc1daa82f860024c9916f2eab04ac50da9"
        private_key = "4d6fbfd1fa028afee050068f08c46b95754fd27a06f429b308ba326fff094349"
        public_key = "10afb6ed5c730bff355db7958ae19a466d4c78be8780db271192eec1b266c2a4"
        # address = "erd1zzhmdm2uwv9l7d2ak72c4cv6gek5c797s7qdkfc3jthvrvnxc2jqdsnp9y"

        actual_mnemonic_seed = mnemonic_to_bip39seed(mnemonic)
        actual_private_key = bip39seed_to_private_key(actual_mnemonic_seed)
        signing_key = nacl.signing.SigningKey(actual_private_key)
        actual_public_key = bytes(signing_key.verify_key)

        self.assertEqual(mnemonic_seed, actual_mnemonic_seed.hex())
        self.assertEqual(private_key, actual_private_key.hex())
        self.assertEqual(public_key, actual_public_key.hex())

        # password = "Password1!"
        # keystore_file = "erd1l4qsjlxuq33dld8ujmqlq3qs45f5qlspy2gvwwamshv2jmfg4g3q77yr0p.json"
        mnemonic = "real reveal sausage puppy artefact chapter original enough cinnamon run pledge awake fall double antenna admit keep melody celery since hood hurry achieve fee"
        mnemonic_seed = "9a8a5cfe7e4e7cfea54431aa80b9179985bfbf0af29ce75aff9bc4f5766ec2f5fb308486bb702e7465467a94792d16fd66f9307a95c1912526d08b21b6cc41b8"
        private_key = "33306aa0bf13a02057ece15e07dc8e9cfff2b77147d5a007d205d782fc90e362"
        public_key = "fd41097cdc0462dfb4fc96c1f04410ad13407e012290c73bbb85d8a96d28aa22"
        # address = "erd1l4qsjlxuq33dld8ujmqlq3qs45f5qlspy2gvwwamshv2jmfg4g3q77yr0p"

        actual_mnemonic_seed = mnemonic_to_bip39seed(mnemonic)
        actual_private_key = bip39seed_to_private_key(actual_mnemonic_seed)
        signing_key = nacl.signing.SigningKey(actual_private_key)
        actual_public_key = bytes(signing_key.verify_key)

        self.assertEqual(mnemonic_seed, actual_mnemonic_seed.hex())
        self.assertEqual(private_key, actual_private_key.hex())
        self.assertEqual(public_key, actual_public_key.hex())
