import logging
from pathlib import Path

from Cryptodome.Hash import keccak
from multiversx_sdk import Account, Address, TransactionsFactoryConfig

from multiversx_sdk_cli.contract_verification import _create_request_signature
from multiversx_sdk_cli.contracts import SmartContract

logging.basicConfig(level=logging.INFO)

testdata_folder = Path(__file__).parent / "testdata"


def test_playground_keccak():
    hexhash = keccak.new(digest_bits=256).update(b"").hexdigest()
    assert hexhash == "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"


def test_contract_verification_create_request_signature():
    account = Account.new_from_pem(file_path=testdata_folder / "walletKey.pem")
    contract_address = Address.from_bech32("erd1qqqqqqqqqqqqqpgqeyj9g344pqguukajpcfqz9p0rfqgyg4l396qespdck")
    request_payload = b"test"
    signature = _create_request_signature(account, contract_address, request_payload)

    assert (
        signature.hex()
        == "30111258cc42ea08e0c6a3e053cc7086a88d614b8b119a244904e9a19896c73295b2fe5c520a1cb07cfe20f687deef9f294a0a05071e85c78a70a448ea5f0605"
    )


def test_prepare_args_for_factories():
    sc = SmartContract(TransactionsFactoryConfig("mock"))
    args = [
        "0x5",
        "123",
        "false",
        "true",
        "str:test-string",
        "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
    ]

    arguments = sc._prepare_args_for_factory(args)
    assert arguments[0].get_payload() == b"\x05"
    assert arguments[1].get_payload() == 123
    assert arguments[2].get_payload() is False
    assert arguments[3].get_payload() is True
    assert arguments[4].get_payload() == "test-string"
    assert (
        arguments[5].get_payload()
        == Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th").get_public_key()
    )
