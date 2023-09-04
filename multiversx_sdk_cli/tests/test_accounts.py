from pathlib import Path

import pytest

from multiversx_sdk_cli.accounts import Account


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
