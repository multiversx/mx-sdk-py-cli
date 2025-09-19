import base64
import json
from pathlib import Path
from typing import Any

from multiversx_sdk_cli.cli import main

testdata = Path(__file__).parent / "testdata"
user = testdata / "testUser.pem"
user_address = "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
grace = "erd1r69gk66fmedhhcg24g2c5kn2f2a5k4kvpr6jfw67dn2lyydd8cfswy6ede"
frank = "erd1kdl46yctawygtwg2k462307dmz2v55c605737dp3zkxh04sct7asqylhyv"


def test_issue_fungible(capsys: Any):
    return_code = main(
        [
            "token",
            "issue-fungible",
            "--token-name",
            "FRANK",
            "--token-ticker",
            "FRANK",
            "--initial-supply",
            "100",
            "--num-decimals",
            "0",
            "--cannot-upgrade",
            "--cannot-add-special-roles",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "50000000000000000"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "issue@4652414e4b@4652414e4b@64@@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@66616c7365@63616e4164645370656369616c526f6c6573@66616c7365"
    )


def test_issue_semi_fungible(capsys: Any):
    return_code = main(
        [
            "token",
            "issue-semi-fungible",
            "--token-name",
            "FRANK",
            "--token-ticker",
            "FRANK",
            "--cannot-upgrade",
            "--cannot-add-special-roles",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "50000000000000000"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "issueSemiFungible@4652414e4b@4652414e4b@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e5472616e736665724e4654437265617465526f6c65@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@66616c7365@63616e4164645370656369616c526f6c6573@66616c7365"
    )


def test_issue_non_fungible(capsys: Any):
    return_code = main(
        [
            "token",
            "issue-non-fungible",
            "--token-name",
            "FRANK",
            "--token-ticker",
            "FRANK",
            "--cannot-upgrade",
            "--cannot-add-special-roles",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "50000000000000000"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "issueNonFungible@4652414e4b@4652414e4b@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e5472616e736665724e4654437265617465526f6c65@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@66616c7365@63616e4164645370656369616c526f6c6573@66616c7365"
    )


def test_register_meta_esdt(capsys: Any):
    return_code = main(
        [
            "token",
            "register-meta-esdt",
            "--token-name",
            "FRANK",
            "--token-ticker",
            "FRANK",
            "--num-decimals",
            "10",
            "--cannot-upgrade",
            "--cannot-add-special-roles",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "50000000000000000"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "registerMetaESDT@4652414e4b@4652414e4b@0a@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e5472616e736665724e4654437265617465526f6c65@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@66616c7365@63616e4164645370656369616c526f6c6573@66616c7365"
    )


def test_register_and_set_all_roles(capsys: Any):
    return_code = main(
        [
            "token",
            "register-and-set-all-roles",
            "--token-name",
            "TEST",
            "--token-ticker",
            "TEST",
            "--num-decimals",
            "2",
            "--token-type",
            "FNG",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "50000000000000000"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "registerAndSetAllRoles@54455354@54455354@464e47@02"


def test_set_special_role_nft(capsys: Any):
    return_code = main(
        [
            "token",
            "set-special-role-nft",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--nft-create",
            "--nft-update-attributes",
            "--nft-add-uri",
            "--esdt-modify-creator",
            "--nft-recreate",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e4654437265617465@45534454526f6c654e465455706461746541747472696275746573@45534454526f6c654e4654416464555249@45534454526f6c654d6f6469667943726561746f72@45534454526f6c654e46545265637265617465"
    )


def test_unset_special_role_nft(capsys: Any):
    return_code = main(
        [
            "token",
            "unset-special-role-nft",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--nft-update-attributes",
            "--nft-add-uri",
            "--esdt-modify-creator",
            "--nft-recreate",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "unSetSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e465455706461746541747472696275746573@45534454526f6c654e4654416464555249@45534454526f6c654d6f6469667943726561746f72@45534454526f6c654e46545265637265617465"
    )


def test_create_nft(capsys: Any):
    return_code = main(
        [
            "token",
            "create-nft",
            "--token-identifier",
            "FRANK-aa9e8d",
            "--initial-quantity",
            "1",
            "--name",
            "test",
            "--royalties",
            "1000",
            "--hash",
            "abba",
            "--attributes",
            "74657374",
            "--uris",
            "a",
            "b",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == user_address
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "ESDTNFTCreate@4652414e4b2d616139653864@01@74657374@03e8@61626261@74657374@61@62"


def test_set_special_role_on_fungible_token(capsys: Any):
    return_code = main(
        [
            "token",
            "set-special-role-fungible",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--local-mint",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654c6f63616c4d696e74"
    )


def test_unset_special_role_on_fungible_token(capsys: Any):
    return_code = main(
        [
            "token",
            "unset-special-role-fungible",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--local-mint",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "unSetSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654c6f63616c4d696e74"
    )


def test_set_all_roles_on_fungible_token(capsys: Any):
    return_code = main(
        [
            "token",
            "set-special-role-fungible",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--local-mint",
            "--local-burn",
            "--esdt-transfer-role",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654c6f63616c4d696e74@45534454526f6c654c6f63616c4275726e@455344545472616e73666572526f6c65"
    )


def test_set_special_roles_on_semi_fungible(capsys: Any):
    return_code = main(
        [
            "token",
            "set-special-role-semi-fungible",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--nft-create",
            "--nft-burn",
            "--nft-add-quantity",
            "--esdt-transfer-role",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e4654437265617465@45534454526f6c654e46544275726e@45534454526f6c654e46544164645175616e74697479@455344545472616e73666572526f6c65"
    )


def test_unset_special_roles_on_semi_fungible(capsys: Any):
    return_code = main(
        [
            "token",
            "unset-special-role-semi-fungible",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--nft-burn",
            "--nft-add-quantity",
            "--esdt-transfer-role",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "unSetSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e46544275726e@45534454526f6c654e46544164645175616e74697479@455344545472616e73666572526f6c65"
    )


def test_set_special_roles_on_meta_esdt(capsys: Any):
    return_code = main(
        [
            "token",
            "set-special-role-meta-esdt",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--nft-create",
            "--nft-burn",
            "--nft-add-quantity",
            "--esdt-transfer-role",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e4654437265617465@45534454526f6c654e46544275726e@45534454526f6c654e46544164645175616e74697479@455344545472616e73666572526f6c65"
    )


def test_unset_special_roles_on_meta_esdt(capsys: Any):
    return_code = main(
        [
            "token",
            "unset-special-role-meta-esdt",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--nft-burn",
            "--nft-add-quantity",
            "--esdt-transfer-role",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "unSetSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e46544275726e@45534454526f6c654e46544164645175616e74697479@455344545472616e73666572526f6c65"
    )


def test_pause_token(capsys: Any):
    return_code = main(
        [
            "token",
            "pause",
            "--token-identifier",
            "FRANK-11ce3e",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "pause@4652414e4b2d313163653365"


def test_unpause_token(capsys: Any):
    return_code = main(
        [
            "token",
            "unpause",
            "--token-identifier",
            "FRANK-11ce3e",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "unPause@4652414e4b2d313163653365"


def test_freeze_token(capsys: Any):
    return_code = main(
        [
            "token",
            "freeze",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "freeze@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13"


def test_unfreeze_token(capsys: Any):
    return_code = main(
        [
            "token",
            "unfreeze",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "unFreeze@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13"


def test_local_mint(capsys: Any):
    return_code = main(
        [
            "token",
            "local-mint",
            "--token-identifier",
            "FRANK-11ce3e",
            "--supply-to-mint",
            "10",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == user_address
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "ESDTLocalMint@4652414e4b2d313163653365@0a"


def test_local_burn(capsys: Any):
    return_code = main(
        [
            "token",
            "local-burn",
            "--token-identifier",
            "FRANK-11ce3e",
            "--supply-to-burn",
            "10",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == user_address
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "ESDTLocalBurn@4652414e4b2d313163653365@0a"


def test_update_attributes(capsys: Any):
    return_code = main(
        [
            "token",
            "update-attributes",
            "--token-identifier",
            "FRANK-11ce3e",
            "--token-nonce",
            "10",
            "--attributes",
            "74657374",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == user_address
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "ESDTNFTUpdateAttributes@4652414e4b2d313163653365@0a@74657374"


def test_add_quantity(capsys: Any):
    return_code = main(
        [
            "token",
            "add-quantity",
            "--token-identifier",
            "FRANK-11ce3e",
            "--token-nonce",
            "10",
            "--quantity",
            "10",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == user_address
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "ESDTNFTAddQuantity@4652414e4b2d313163653365@0a@0a"


def test_burn_quantity(capsys: Any):
    return_code = main(
        [
            "token",
            "burn-quantity",
            "--token-identifier",
            "FRANK-11ce3e",
            "--token-nonce",
            "10",
            "--quantity",
            "10",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == user_address
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "ESDTNFTBurn@4652414e4b2d313163653365@0a@0a"


def test_set_burn_role_globally(capsys: Any):
    return_code = main(
        [
            "token",
            "set-burn-role-globally",
            "--token-identifier",
            "FRANK-11ce3e",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "setBurnRoleGlobally@4652414e4b2d313163653365"


def test_unset_burn_role_globally(capsys: Any):
    return_code = main(
        [
            "token",
            "unset-burn-role-globally",
            "--token-identifier",
            "FRANK-11ce3e",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "unsetBurnRoleGlobally@4652414e4b2d313163653365"


def test_wipe(capsys: Any):
    return_code = main(
        [
            "token",
            "wipe",
            "--token-identifier",
            "FRANK-11ce3e",
            "--user",
            grace,
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "wipe@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13"


def test_modify_royalties(capsys: Any):
    return_code = main(
        [
            "token",
            "modify-royalties",
            "--token-identifier",
            "TEST-123456",
            "--token-nonce",
            "1",
            "--royalties",
            "1234",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == user_address
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "ESDTModifyRoyalties@544553542d313233343536@01@04d2"


def test_set_new_uris(capsys: Any):
    return_code = main(
        [
            "token",
            "set-new-uris",
            "--token-identifier",
            "TEST-123456",
            "--token-nonce",
            "1",
            "--uris",
            "firstURI",
            "secondURI",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == user_address
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "ESDTSetNewURIs@544553542d313233343536@01@6669727374555249@7365636f6e64555249"


def test_modify_creator(capsys: Any):
    return_code = main(
        [
            "token",
            "modify-creator",
            "--token-identifier",
            "TEST-123456",
            "--token-nonce",
            "1",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == user_address
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "ESDTModifyCreator@544553542d313233343536@01"


def test_update_metadata(capsys: Any):
    return_code = main(
        [
            "token",
            "update-metadata",
            "--token-identifier",
            "TEST-123456",
            "--token-nonce",
            "1",
            "--token-name",
            "Test",
            "--royalties",
            "1234",
            "--hash",
            "abba",
            "--attributes",
            "74657374",
            "--uris",
            "firstURI",
            "secondURI",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == user_address
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "ESDTMetaDataUpdate@544553542d313233343536@01@54657374@04d2@61626261@74657374@6669727374555249@7365636f6e64555249"
    )


def test_recreate_metadata(capsys: Any):
    return_code = main(
        [
            "token",
            "nft-metadata-recreate",
            "--token-identifier",
            "TEST-123456",
            "--token-nonce",
            "1",
            "--token-name",
            "Test",
            "--royalties",
            "1234",
            "--hash",
            "abba",
            "--attributes",
            "74657374",
            "--uris",
            "firstURI",
            "secondURI",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == user_address
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "ESDTMetaDataRecreate@544553542d313233343536@01@54657374@04d2@61626261@74657374@6669727374555249@7365636f6e64555249"
    )


def test_change_token_to_dynamic(capsys: Any):
    return_code = main(
        [
            "token",
            "change-to-dynamic",
            "--token-identifier",
            "TEST-123456",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "changeToDynamic@544553542d313233343536"


def test_update_token_id(capsys: Any):
    return_code = main(
        [
            "token",
            "update-token-id",
            "--token-identifier",
            "TEST-123456",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "updateTokenID@544553542d313233343536"


def test_register_dynamic(capsys: Any):
    return_code = main(
        [
            "token",
            "register-dynamic",
            "--token-name",
            "Test",
            "--token-ticker",
            "TEST-123456",
            "--token-type",
            "SFT",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "50000000000000000"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "registerDynamic@54657374@544553542d313233343536@534654"


def test_register_dynamic_and_set_all_roles(capsys: Any):
    return_code = main(
        [
            "token",
            "register-dynamic-and-set-all-roles",
            "--token-name",
            "Test",
            "--token-ticker",
            "TEST-123456",
            "--token-type",
            "SFT",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "50000000000000000"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "registerAndSetAllRolesDynamic@54657374@544553542d313233343536@534654"


def test_register_dynamic_meta_esdt(capsys: Any):
    return_code = main(
        [
            "token",
            "register-dynamic",
            "--token-name",
            "Test",
            "--token-ticker",
            "TEST-987654",
            "--token-type",
            "META",
            "--denominator",
            "18",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "50000000000000000"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "registerDynamic@54657374@544553542d393837363534@4d455441@12"


def test_register_dynamic_and_set_all_roles_meta_esdt(capsys: Any):
    return_code = main(
        [
            "token",
            "register-dynamic-and-set-all-roles",
            "--token-name",
            "Test",
            "--token-ticker",
            "TEST-987654",
            "--token-type",
            "META",
            "--denominator",
            "18",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "50000000000000000"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "registerAndSetAllRolesDynamic@54657374@544553542d393837363534@4d455441@12"


def test_transfer_ownership(capsys: Any):
    return_code = main(
        [
            "token",
            "transfer-ownership",
            "--token-identifier",
            "AND-1d56f2",
            "--new-owner",
            frank,
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "transferOwnership@414e442d316435366632@b37f5d130beb8885b90ab574a8bfcdd894ca531a7d3d1f3431158d77d6185fbb"
    )


def test_freeze_single_nft(capsys: Any):
    return_code = main(
        [
            "token",
            "freeze-single-nft",
            "--token-identifier",
            "TEST-123456",
            "--token-nonce",
            "1",
            "--user",
            frank,
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "freezeSingleNFT@544553542d313233343536@01@b37f5d130beb8885b90ab574a8bfcdd894ca531a7d3d1f3431158d77d6185fbb"
    )


def test_unfreeze_single_nft(capsys: Any):
    return_code = main(
        [
            "token",
            "unfreeze-single-nft",
            "--token-identifier",
            "TEST-123456",
            "--token-nonce",
            "1",
            "--user",
            frank,
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "unFreezeSingleNFT@544553542d313233343536@01@b37f5d130beb8885b90ab574a8bfcdd894ca531a7d3d1f3431158d77d6185fbb"
    )


def test_change_sft_to_meta_esdt(capsys: Any):
    return_code = main(
        [
            "token",
            "change-sft-to-meta-esdt",
            "--collection",
            "SFT-123456",
            "--decimals",
            "6",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "changeSFTToMetaESDT@5346542d313233343536@06"


def test_transfer_nft_create_role(capsys: Any):
    return_code = main(
        [
            "token",
            "transfer-nft-create-role",
            "--token-identifier",
            "SFT-123456",
            "--user",
            frank,
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data
        == "transferNFTCreateRole@5346542d313233343536@c0006edaaee4fd479f2f248b341eb11eaecaec4d7dee190619958332bba5200f@b37f5d130beb8885b90ab574a8bfcdd894ca531a7d3d1f3431158d77d6185fbb"
    )


def test_stop_nft_create(capsys: Any):
    return_code = main(
        [
            "token",
            "stop-nft-creation",
            "--token-identifier",
            "SFT-123456",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "stopNFTCreate@5346542d313233343536"


def test_wipe_single_nft(capsys: Any):
    return_code = main(
        [
            "token",
            "wipe-single-nft",
            "--token-identifier",
            "SFT-123456",
            "--token-nonce",
            "10",
            "--user",
            frank,
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert (
        data == "wipeSingleNFT@5346542d313233343536@0a@b37f5d130beb8885b90ab574a8bfcdd894ca531a7d3d1f3431158d77d6185fbb"
    )


def test_add_uris(capsys: Any):
    return_code = main(
        [
            "token",
            "add-uris",
            "--token-identifier",
            "SFT-123456",
            "--token-nonce",
            "10",
            "--uris",
            "firstURI",
            "secondURI",
            "--pem",
            str(user),
            "--nonce",
            "7",
            "--chain",
            "D",
        ]
    )
    assert not return_code

    transaction = get_transaction(capsys)
    assert transaction["sender"] == user_address
    assert transaction["receiver"] == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
    assert transaction["value"] == "0"
    assert transaction["chainID"] == "D"
    data = base64.b64decode(transaction["data"]).decode()
    assert data == "ESDTNFTAddURI@5346542d313233343536@0a@6669727374555249@7365636f6e64555249"


def _read_stdout(capsys: Any) -> str:
    stdout: str = capsys.readouterr().out.strip()
    return stdout


def get_transaction(capsys: Any) -> dict[str, Any]:
    out = _read_stdout(capsys)
    output: dict[str, Any] = json.loads(out)
    tx: dict[str, Any] = output["emittedTransaction"]
    return tx
