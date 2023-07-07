from pathlib import Path

import pytest

from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.transactions import Transaction


def test_sign_transaction():
    alice_pem = Path(__file__).parent / "testdata" / "alice.pem"
    alice = Account(pem_file=str(alice_pem))

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
    transaction.signature = alice.sign_transaction(transaction)

    assert "0e69f27e24aba2f3b7a8842dc7e7c085a0bfb5b29112b258318eed73de9c8809889756f8afaa74c7b3c7ce20a028b68ba90466a249aaf999a1a78dcf7f4eb40c" == transaction.signature

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
    transaction.signature = alice.sign_transaction(transaction)

    assert "83efd1bc35790ecc220b0ed6ddd1fcb44af6653dd74e37b3a49dcc1f002a1b98b6f79779192cca68bdfefd037bc81f4fa606628b751023122191f8c062362805" == transaction.signature


def test_sign_message():
    alice_pem = Path(__file__).parent / "testdata" / "alice.pem"
    alice = Account(pem_file=str(alice_pem))

    message = b"hello"
    signature = alice.sign_message(message)
    assert signature == "561bc58f1dc6b10de208b2d2c22c9a474ea5e8cabb59c3d3ce06bbda21cc46454aa71a85d5a60442bd7784effa2e062fcb8fb421c521f898abf7f5ec165e5d0f"


def test_load_account_from_keystore_without_kind():
    alice_json = Path(__file__).parent / "testdata" / "alice.json"
    account = Account(key_file=str(alice_json), password="password")
    assert account.address.bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

    with pytest.raises(Exception):
        _ = Account(key_file=str(alice_json), password="wrong_password")


def test_load_account_from_keystore_with_kind_secret_key():
    keystore_path = Path(__file__).parent / "testdata" / "aliceWithKindSecretKey.json"
    account = Account(key_file=str(keystore_path), password="password")
    assert account.address.bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

    with pytest.raises(Exception):
        _ = Account(key_file=str(keystore_path), password="wrong_password")


def test_load_account_from_keystore_with_kind_mnemonic():
    keystore_path = Path(__file__).parent / "testdata" / "withDummyMnemonic.json"
    account = Account(key_file=str(keystore_path), password="password")
    assert account.address.bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

    with pytest.raises(Exception):
        _ = Account(key_file=str(keystore_path), password="wrong_password")
