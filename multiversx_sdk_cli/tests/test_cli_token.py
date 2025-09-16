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
            "--can-not-upgrade",
            "--can-not-add-special-roles",
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
            "--can-not-upgrade",
            "--can-not-add-special-roles",
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
            "--can-not-upgrade",
            "--can-not-add-special-roles",
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
            "--can-not-upgrade",
            "--can-not-add-special-roles",
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


def _read_stdout(capsys: Any) -> str:
    stdout: str = capsys.readouterr().out.strip()
    return stdout


def get_transaction(capsys: Any) -> dict[str, Any]:
    out = _read_stdout(capsys)
    output: dict[str, Any] = json.loads(out)
    tx: dict[str, Any] = output["emittedTransaction"]
    return tx
