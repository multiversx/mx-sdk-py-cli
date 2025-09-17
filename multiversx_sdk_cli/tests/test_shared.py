from multiversx_sdk import Address

from multiversx_sdk_cli.args_converter import convert_args_to_typed_values
from multiversx_sdk_cli.cli_shared import prepare_token_transfers


def test_prepare_token_tranfers():
    # list of token transfers as interpreted by the CLI
    token_transfers = [
        "FNG-123456",
        "10000",
        "SFT-123123-0a",
        "3",
        "NFT-987654-07",
        "1",
        "META-777777-10",
        "123456789",
    ]
    transfers = prepare_token_transfers(token_transfers)

    assert len(transfers) == 4
    assert transfers[0].token.identifier == "FNG-123456"
    assert transfers[0].token.nonce == 0
    assert transfers[0].amount == 10000

    assert transfers[1].token.identifier == "SFT-123123"
    assert transfers[1].token.nonce == 10
    assert transfers[1].amount == 3

    assert transfers[2].token.identifier == "NFT-987654"
    assert transfers[2].token.nonce == 7
    assert transfers[2].amount == 1

    assert transfers[3].token.identifier == "META-777777"
    assert transfers[3].token.nonce == 16
    assert transfers[3].amount == 123456789


def test_prepare_args_for_factories():
    args = [
        "0x5",
        "123",
        "false",
        "true",
        "str:test-string",
        "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
    ]

    arguments = convert_args_to_typed_values(args)
    assert arguments[0].get_payload() == b"\x05"
    assert arguments[1].get_payload() == 123
    assert arguments[2].get_payload() is False
    assert arguments[3].get_payload() is True
    assert arguments[4].get_payload() == "test-string"
    assert (
        arguments[5].get_payload()
        == Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th").get_public_key()
    )
