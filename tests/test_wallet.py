import logging
import unittest
from pathlib import Path
from typing import Any

import nacl.encoding
import nacl.signing
from erdpy import utils
from erdpy.accounts import Account, Address
from erdpy.transactions import Transaction
from erdpy.wallet import (bip39seed_to_private_key, generate_pair,
                          mnemonic_to_bip39seed, pem)

logging.basicConfig(level=logging.INFO)


class WalletTestCase(unittest.TestCase):
    def setUp(self):
        self.testdata = Path(__file__).parent.joinpath("testdata")
        self.testdata_out = Path(__file__).parent.joinpath("testdata-out")
        utils.ensure_folder(self.testdata_out)

        self.alice = Account(pem_file=str(self.testdata.joinpath("keys", "alice.pem")))

    def test_nacl_playground_signing(self):
        private_key_hex = "b8211b08edc8aca591bedf1b9aba47e4077e54ac7d4ceb2f1bc9e10c064d3e6c7a5679a427f6df7adf2310ddf5e570fd51e47e6b1511124d6b250b989b017588"
        private_key_bytes = bytes.fromhex(private_key_hex)
        private_key_seed_bytes = private_key_bytes[:32]
        signing_key: Any = nacl.signing.SigningKey(private_key_seed_bytes)
        signed = signing_key.sign(b"test")
        signature = signed.signature
        signed_bytes_hex = signature.hex()

        self.assertEqual("a4918458d874ca58893a1f92dac33e7b10e3bf46048ad5de5bc260487ca84e8e07603297120fdc018242f63bd8e87b13efd108f8ffa095f536b6eda03805590c", signed_bytes_hex)
        self.assertEqual(64, len(signature))

    def test_pem_get_pubkey(self):
        pem_file = self.testdata.joinpath("keys", "alice.pem")
        address = pem.get_pubkey(pem_file)

        self.assertEqual("fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293", address.hex())

    def test_pem_parse_multiple(self):
        pem_file = self.testdata.joinpath("keys", "walletKey.pem")

        seed, address = pem.parse(pem_file, index=0)
        self.assertEqual("1f4dd8b7d18b5d0785c9d0802ec14d553dba356812b85c7e3414373388472010", seed.hex())
        self.assertEqual(Address("erd1sjsk3n2d0krq3pyxxtgf0q7j3t56sgusqaujj4n82l39t9h7jers6gslr4").hex(), address.hex())

        seed, address = pem.parse(pem_file, index=1)
        self.assertEqual("2565dbbdb62301e4c7b12b8a41cd3b2fbd7ae687c8d9741937aa48cf246aeb25", seed.hex())
        self.assertEqual(Address("erd10536tc3s886yqxtln74u6mztuwl5gy9k9gp8fttxda0klgxg979srtg5wt").hex(), address.hex())

        seed, address = pem.parse(pem_file, index=2)
        self.assertEqual("08de69d398f4a5ffdce0f1a8569704dbc8b58aaf7ba3e726134e32f1e8bf04ad", seed.hex())
        self.assertEqual(Address("erd1n230jlgfepdvf28vqt3zeawexg2jhvxqxjuqdfsss0xc62xcqcps9k54ag").hex(), address.hex())

        seed, address = pem.parse(pem_file, index=3)
        self.assertEqual("4d9dcc1c09a6d00c4c9a389e662d9fe26e0bf4c859776d4d338b5a9c41fc12d4", seed.hex())
        self.assertEqual(Address("erd143907zxv0ujxr9q4mda7rmczn2xwhmqn7p9lfz666z8hd2lcks2szt5yql").hex(), address.hex())

    def test_pem_parse(self):
        pem_file = self.testdata.joinpath("keys", "alice.pem")
        seed, address = pem.parse(pem_file)

        self.assertEqual("1a927e2af5306a9bb2ea777f73e06ecc0ac9aaa72fb4ea3fecf659451394cccf", seed.hex())
        self.assertEqual("fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293", address.hex())

    def test_serialize_transaction_payload(self):
        # With data field
        transaction = Transaction()
        transaction.nonce = 0
        transaction.value = "42"
        transaction.sender = "alice"
        transaction.receiver = "bob"
        transaction.gasPrice = 43
        transaction.gasLimit = 44
        transaction.data = "foobar"
        transaction.chainID = "BoN"
        transaction.version = 1
        serialized = transaction.serialize().decode()
        self.assertEqual("""{"nonce":0,"value":"42","receiver":"bob","sender":"alice","gasPrice":43,"gasLimit":44,"data":"Zm9vYmFy","chainID":"BoN","version":1}""", serialized)

        # Without data field
        transaction.data = ""
        serialized = transaction.serialize().decode()
        self.assertEqual("""{"nonce":0,"value":"42","receiver":"bob","sender":"alice","gasPrice":43,"gasLimit":44,"chainID":"BoN","version":1}""", serialized)

        # With actual addresses
        transaction = Transaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = "foo"
        transaction.chainID = "BoN"
        transaction.version = 1
        serialized = transaction.serialize().decode()
        self.assertEqual("""{"nonce":0,"value":"0","receiver":"erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr","sender":"erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz","gasPrice":200000000000000,"gasLimit":500000000,"data":"Zm9v","chainID":"BoN","version":1}""", serialized)

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

        self.assertEqual("f9878caeba4285a9fe66fa8127eb9f7e3f178de40f96727f639e31f0a503efd154d73752781ad06c788876342df39cec27863f5dd88e23c33a4f5a0c57015905", transaction.signature)

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

        self.assertEqual("1ad14993a3cf6a5e0898a29271a2924fc34f80ba2a391dd2ff5c2fcc554e5a71eda0e34044f99888ec1a1da6d4cf82345e848cec69ccd27e192f8b66c4beaa0c", transaction.signature)    

    def test_sign_transaction_trust_wallet_scenario(self):
        # With data
        transaction = Transaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"
        transaction.gasPrice = 1000000000
        transaction.gasLimit = 50000
        transaction.data = "foo"
        transaction.chainID = "1"
        transaction.version = 1
        transaction.sign(self.alice)
        serialized = transaction.serialize().decode()

        self.assertEqual("""{"nonce":0,"value":"0","receiver":"erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r","sender":"erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz","gasPrice":1000000000,"gasLimit":50000,"data":"Zm9v","chainID":"1","version":1,"signature":"b5fddb8c16fa7f6123cb32edc854f1e760a3eb62c6dc420b5a4c0473c58befd45b621b31a448c5b59e21428f2bc128c80d0ee1caa4f2bf05a12be857ad451b00"}""", serialized)
        self.assertEqual("b5fddb8c16fa7f6123cb32edc854f1e760a3eb62c6dc420b5a4c0473c58befd45b621b31a448c5b59e21428f2bc128c80d0ee1caa4f2bf05a12be857ad451b00", transaction.signature)

        # Without data
        transaction = Transaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"
        transaction.gasPrice = 1000000000
        transaction.gasLimit = 50000
        transaction.data = ""
        transaction.chainID = "1"
        transaction.version = 1
        transaction.sign(self.alice)
        serialized = transaction.serialize().decode()

        self.assertEqual("""{"nonce":0,"value":"0","receiver":"erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r","sender":"erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz","gasPrice":1000000000,"gasLimit":50000,"chainID":"1","version":1,"signature":"3079d37bfbdbe66fbb4c4b186144f9d9ad5b4b08fbcd6083be0688cf1171123109dfdefdbabf91425c757ca109b6db6d674cb9aeebb19a1a51333565abb53109"}""", serialized)
        self.assertEqual("3079d37bfbdbe66fbb4c4b186144f9d9ad5b4b08fbcd6083be0688cf1171123109dfdefdbabf91425c757ca109b6db6d674cb9aeebb19a1a51333565abb53109", transaction.signature)

    def test_sign_transaction_docs_scenario(self):
        # With data
        transaction = Transaction()
        transaction.nonce = 7
        transaction.value = "10000000000000000000"  # 10 ERD
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"
        transaction.gasPrice = 1000000000
        transaction.gasLimit = 70000
        transaction.data = "for the book"
        transaction.chainID = "1"
        transaction.version = 1
        serialized = transaction.serialize().decode()
        transaction.sign(self.alice)

        self.assertEqual("""{"nonce":7,"value":"10000000000000000000","receiver":"erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r","sender":"erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz","gasPrice":1000000000,"gasLimit":70000,"data":"Zm9yIHRoZSBib29r","chainID":"1","version":1}""", serialized)
        self.assertEqual("1702bb7696f992525fb77597956dd74059b5b01e88c813066ad1f6053c6afca97d6eaf7039b2a21cccc7d73b3e5959be4f4c16f862438c7d61a30c91e3d16c01", transaction.signature)

        # Without data
        transaction = Transaction()
        transaction.nonce = 8
        transaction.value = "10000000000000000000"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"
        transaction.gasPrice = 1000000000
        transaction.gasLimit = 50000
        transaction.data = ""
        transaction.chainID = "1"
        transaction.version = 1
        serialized = transaction.serialize().decode()
        transaction.sign(self.alice)

        self.assertEqual("""{"nonce":8,"value":"10000000000000000000","receiver":"erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r","sender":"erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz","gasPrice":1000000000,"gasLimit":50000,"chainID":"1","version":1}""", serialized)
        self.assertEqual("4a6d8186eae110894e7417af82c9bf9592696c0600faf110972e0e5310d8485efc656b867a2336acec2b4c1e5f76c9cc70ba1803c6a46455ed7f1e2989a90105", transaction.signature)

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
        signing_key: Any = nacl.signing.SigningKey(actual_private_key)
        actual_public_key = bytes(signing_key.verify_key)

        self.assertEqual(mnemonic_seed, actual_mnemonic_seed.hex())
        self.assertEqual(private_key, actual_private_key.hex())
        self.assertEqual(public_key, actual_public_key.hex())
