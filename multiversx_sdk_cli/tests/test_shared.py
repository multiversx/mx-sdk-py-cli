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
