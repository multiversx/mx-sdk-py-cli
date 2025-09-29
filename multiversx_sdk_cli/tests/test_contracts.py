import logging
from pathlib import Path

from Cryptodome.Hash import keccak
from multiversx_sdk import Account, Address

from multiversx_sdk_cli.contract_verification import _create_request_signature

logging.basicConfig(level=logging.INFO)

testdata_folder = Path(__file__).parent / "testdata"


def test_playground_keccak():
    hexhash = keccak.new(digest_bits=256).update(b"").hexdigest()
    assert hexhash == "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"


def test_contract_verification_create_request_signature():
    account = Account.new_from_pem(file_path=testdata_folder / "walletKey.pem")
    contract_address = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqeyj9g344pqguukajpcfqz9p0rfqgyg4l396qespdck")
    request_payload = b"test"
    signature = _create_request_signature(account, contract_address, request_payload)

    assert (
        signature.hex()
        == "30111258cc42ea08e0c6a3e053cc7086a88d614b8b119a244904e9a19896c73295b2fe5c520a1cb07cfe20f687deef9f294a0a05071e85c78a70a448ea5f0605"
    )
