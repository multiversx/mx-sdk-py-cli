import base64
import json
from pathlib import Path
from typing import Any

from multiversx_sdk_cli.cli import main

testdata = Path(__file__).parent / "testdata"
user = testdata / "testUser.pem"
user_address = "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
multisig_abi = testdata / "multisig.abi.json"
contract_address = "erd1qqqqqqqqqqqqqpgqe832k3l6d02ww7l9cvqum25539nmmdxa9ncsdutjuf"
contract_address_hex = "00000000000000000500c9e2ab47fa6bd4e77be5c301cdaa948967bdb4dd2cf1"
bob = "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"


def test_deploy_multisig(capsys: Any):
    multisig_bytecode = (testdata / "multisig.wasm").read_bytes()

    return_code = main(
        [
            "multisig",
            "deploy",
            "--bytecode",
            str(testdata / "multisig.wasm"),
            "--abi",
            str(multisig_abi),
            "--quorum",
            "1",
            "--board-members",
            user_address,
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "100000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6gq4hu"
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 100_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert f"{multisig_bytecode.hex()}@0500@0504@02@c0006edaaee4fd479f2f248b341eb11eaecaec4d7dee190619958332bba5200f"


def test_deposit_native_token(capsys: Any):
    return_code = main(
        [
            "multisig",
            "deposit",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "60000000",
            "--chain",
            "D",
            "--value",
            "1000000000000000000",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "1000000000000000000"
    assert tx["gasLimit"] == 60_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "deposit"


def test_deposit_esdt(capsys: Any):
    return_code = main(
        [
            "multisig",
            "deposit",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "60000000",
            "--chain",
            "D",
            "--token-transfers",
            "MYTKN-a584f9",
            "100000",
            "SFT-1bc261-01",
            "1",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == user_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 60_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert (
        data
        == f"MultiESDTNFTTransfer@{contract_address_hex}@02@4d59544b4e2d613538346639@@0186a0@5346542d316263323631@01@01@6465706f736974"
    )


def test_discard_action(capsys: Any):
    return_code = main(
        [
            "multisig",
            "discard-action",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--action",
            "7",
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "60000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 60_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "discardAction@07"


def test_discard_batch(capsys: Any):
    return_code = main(
        [
            "multisig",
            "discard-batch",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--action-ids",
            "7",
            "8",
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "60000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 60_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "discardBatch@07@08"


def test_add_board_member(capsys: Any):
    return_code = main(
        [
            "multisig",
            "add-board-member",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--board-member",
            bob,
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "60000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 60_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "proposeAddBoardMember@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"


def test_add_proposer(capsys: Any):
    return_code = main(
        [
            "multisig",
            "add-proposer",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--proposer",
            bob,
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "60000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 60_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "proposeAddProposer@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"


def test_remove_user(capsys: Any):
    return_code = main(
        [
            "multisig",
            "remove-user",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--user",
            bob,
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "60000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 60_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "proposeRemoveUser@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"


def _read_stdout(capsys: Any) -> str:
    stdout: str = capsys.readouterr().out.strip()
    return stdout


def get_transaction(capsys: Any) -> dict[str, Any]:
    out = _read_stdout(capsys)
    output: dict[str, Any] = json.loads(out)
    return output["emittedTransaction"]
