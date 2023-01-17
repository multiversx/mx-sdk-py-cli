import logging

import nacl.signing
from multiversx_sdk_cli.accounts import Account, Address
from multiversx_sdk_cli.errors import GasLimitTooLarge
from multiversx_sdk_cli.tests.utils import MyTestCase
from multiversx_sdk_cli.transactions import Transaction
from multiversx_sdk_cli.wallet import pem

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

    def test_pem_get_pubkey(self):
        pem_file = self.devnet_wallets.joinpath("users", "alice.pem")
        address = pem.get_pubkey(pem_file)

        self.assertEqual("0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1", address.hex())

    def test_pem_parse_multiple(self):
        pem_file = self.testdata.joinpath("walletKey.pem")

        secret_key, address = pem.parse(pem_file, index=0)
        self.assertEqual("1f4dd8b7d18b5d0785c9d0802ec14d553dba356812b85c7e3414373388472010", secret_key.hex())
        self.assertEqual(Address("erd1sjsk3n2d0krq3pyxxtgf0q7j3t56sgusqaujj4n82l39t9h7jers6gslr4").hex(), address.hex())

        secret_key, address = pem.parse(pem_file, index=1)
        self.assertEqual("2565dbbdb62301e4c7b12b8a41cd3b2fbd7ae687c8d9741937aa48cf246aeb25", secret_key.hex())
        self.assertEqual(Address("erd10536tc3s886yqxtln74u6mztuwl5gy9k9gp8fttxda0klgxg979srtg5wt").hex(), address.hex())

        secret_key, address = pem.parse(pem_file, index=2)
        self.assertEqual("08de69d398f4a5ffdce0f1a8569704dbc8b58aaf7ba3e726134e32f1e8bf04ad", secret_key.hex())
        self.assertEqual(Address("erd1n230jlgfepdvf28vqt3zeawexg2jhvxqxjuqdfsss0xc62xcqcps9k54ag").hex(), address.hex())

        secret_key, address = pem.parse(pem_file, index=3)
        self.assertEqual("4d9dcc1c09a6d00c4c9a389e662d9fe26e0bf4c859776d4d338b5a9c41fc12d4", secret_key.hex())
        self.assertEqual(Address("erd143907zxv0ujxr9q4mda7rmczn2xwhmqn7p9lfz666z8hd2lcks2szt5yql").hex(), address.hex())

    def test_pem_parse(self):
        pem_file = self.devnet_wallets.joinpath("users", "alice.pem")
        secret_key, address = pem.parse(pem_file)

        self.assertEqual("413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9", secret_key.hex())
        self.assertEqual("0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1", address.hex())

    def test_parse_validator_pem_default_index(self):
        pem_file = self.multiple_bls_keys_file
        secret_key_bytes, bls_key = pem.parse_validator_pem(pem_file)

        secret_key_hex = bytes.hex(secret_key_bytes)

        self.assertEqual(
            "f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d",
            bls_key)
        self.assertEqual(
            "37633139626633613063353763646431666230386534363037636562616133363437643662393236316234363933663631653936653534623231386434343261",
            secret_key_hex)

    def test_parse_validator_pem_n_index(self):
        pem_file = self.multiple_bls_keys_file
        secret_key_bytes, bls_key = pem.parse_validator_pem(pem_file, 3)

        secret_key_hex = bytes.hex(secret_key_bytes)

        self.assertEqual(
            "12773304cb718250edd89770cedcbf675ccdb7fe2b30bd3185ca65ffa0d516879768ed03f92e41a6e5bc5340b78a9d02655e3b727c79730ead791fb68eaa02b84e1be92a816a9604a1ab9a6d3874b638487e2145239438a4bafac3889348d405",
            bls_key)
        self.assertEqual(
            "38656265623037643239366164323532393430306234303638376137343161313335663833353766373966333966636232383934613666393730336135383136",
            secret_key_hex)

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
