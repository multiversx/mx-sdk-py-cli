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
adder_abi = testdata / "adder.abi.json"


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


def test_change_quorum(capsys: Any):
    return_code = main(
        [
            "multisig",
            "change-quorum",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--quorum",
            "10",
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
    assert data == "proposeChangeQuorum@0a"


def test_transfer_and_execute_with_abi(capsys: Any):
    return_code = main(
        [
            "multisig",
            "transfer-and-execute",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--opt-gas-limit",
            "1000000",
            "--contract-abi",
            str(adder_abi),
            "--function",
            "add",
            "--arguments",
            "7",
            "--receiver",
            "erd1qqqqqqqqqqqqqpgq0rffvv4vk9vesqplv9ws55fxzdfaspqa8cfszy2hms",
            "--value",
            "1000000000000000000",
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
    assert (
        data
        == "proposeTransferExecute@0000000000000000050078d29632acb15998003f615d0a51261353d8041d3e13@0de0b6b3a7640000@0100000000000f4240@616464@07"
    )


def test_transfer_and_execute_without_abi(capsys: Any):
    return_code = main(
        [
            "multisig",
            "transfer-and-execute",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--opt-gas-limit",
            "1000000",
            "--function",
            "add",
            "--arguments",
            "0x07",
            "--receiver",
            "erd1qqqqqqqqqqqqqpgq0rffvv4vk9vesqplv9ws55fxzdfaspqa8cfszy2hms",
            "--value",
            "1000000000000000000",
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
    assert (
        data
        == "proposeTransferExecute@0000000000000000050078d29632acb15998003f615d0a51261353d8041d3e13@0de0b6b3a7640000@0100000000000f4240@616464@07"
    )


def test_transfer_and_execute_without_execute(capsys: Any):
    return_code = main(
        [
            "multisig",
            "transfer-and-execute",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--receiver",
            "erd1qqqqqqqqqqqqqpgq0rffvv4vk9vesqplv9ws55fxzdfaspqa8cfszy2hms",
            "--value",
            "1000000000000000000",
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
    assert (
        data
        == "proposeTransferExecute@0000000000000000050078d29632acb15998003f615d0a51261353d8041d3e13@0de0b6b3a7640000@"
    )


def test_transfer_and_execute_esdt(capsys: Any):
    return_code = main(
        [
            "multisig",
            "transfer-and-execute-esdt",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--token-transfers",
            "ALICE-5627f1",
            "10",
            "--opt-gas-limit",
            "5000000",
            "--function",
            "distribute",
            "--receiver",
            "erd1qqqqqqqqqqqqqpgqfxlljcaalgl2qfcnxcsftheju0ts36kvl3ts3qkewe",
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
    assert (
        data
        == "proposeTransferExecuteEsdt@0000000000000000050049bff963bdfa3ea02713362095df32e3d708eaccfc57@0000000c414c4943452d3536323766310000000000000000000000010a@0100000000004c4b40@3634363937333734373236393632373537343635"
    )


def test_async_call(capsys: Any):
    return_code = main(
        [
            "multisig",
            "async-call",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--opt-gas-limit",
            "5000000",
            "--contract-abi",
            str(adder_abi),
            "--function",
            "add",
            "--arguments",
            "7",
            "--receiver",
            "erd1qqqqqqqqqqqqqpgqdvmhpxxmwv2vfz3sfpggzfyl5qznuz5x05vq5y37ql",
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
    assert (
        data
        == "proposeAsyncCall@000000000000000005006b377098db7314c48a30485081249fa0053e0a867d18@@0100000000004c4b40@616464@07"
    )


def test_sc_deploy_from_source(capsys: Any):
    return_code = main(
        [
            "multisig",
            "deploy-from-source",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--contract-to-copy",
            "erd1qqqqqqqqqqqqqpgqsuxsgykwm6r3s5apct2g5a2rcpe7kw0ed8ssf6h9f6",
            "--contract-abi",
            str(adder_abi),
            "--arguments",
            "0",
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "60000000",
            "--chain",
            "D",
            "--value",
            "50000000000000000",
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
    assert (
        data
        == "proposeSCDeployFromSource@b1a2bc2ec50000@00000000000000000500870d0412cede871853a1c2d48a7543c073eb39f969e1@0500@"
    )


def test_sc_upgrade_from_source(capsys: Any):
    return_code = main(
        [
            "multisig",
            "upgrade-from-source",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--contract-to-upgrade",
            "erd1qqqqqqqqqqqqqpgqsuxsgykwm6r3s5apct2g5a2rcpe7kw0ed8ssf6h9f6",
            "--contract-to-copy",
            "erd1qqqqqqqqqqqqqpgqsuxsgykwm6r3s5apct2g5a2rcpe7kw0ed8ssf6h9f6",
            "--arguments",
            "0x00",
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "60000000",
            "--chain",
            "D",
            "--value",
            "50000000000000000",
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
    assert (
        data
        == "proposeSCUpgradeFromSource@00000000000000000500870d0412cede871853a1c2d48a7543c073eb39f969e1@b1a2bc2ec50000@00000000000000000500870d0412cede871853a1c2d48a7543c073eb39f969e1@0500@00"
    )


def test_sign_action(capsys: Any):
    return_code = main(
        [
            "multisig",
            "sign-action",
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
            "1000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 1_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "sign@07"


def test_sign_batch(capsys: Any):
    return_code = main(
        [
            "multisig",
            "sign-batch",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--batch",
            "7",
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "1000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 1_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "signBatch@07"


def test_sign_and_perform(capsys: Any):
    return_code = main(
        [
            "multisig",
            "sign-and-perform",
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
            "1000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 1_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "signAndPerform@07"


def test_sign_batch_and_perform(capsys: Any):
    return_code = main(
        [
            "multisig",
            "sign-batch-and-perform",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--batch",
            "7",
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "1000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 1_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "signBatchAndPerform@07"


def test_unsign_action(capsys: Any):
    return_code = main(
        [
            "multisig",
            "unsign-action",
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
            "1000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 1_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "unsign@07"


def test_unsign_batch(capsys: Any):
    return_code = main(
        [
            "multisig",
            "unsign-batch",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--batch",
            "7",
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "1000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 1_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "unsignBatch@07"


def test_unsign_for_outdated_board_members(capsys: Any):
    return_code = main(
        [
            "multisig",
            "unsign-for-outdated-members",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--action",
            "7",
            "--outdated-members",
            "1",
            "2",
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "1000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 1_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "unsignForOutdatedBoardMembers@07@01@02"


def test_perform_action(capsys: Any):
    return_code = main(
        [
            "multisig",
            "perform-action",
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
            "1000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 1_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "performAction@07"


def test_perform_batch(capsys: Any):
    return_code = main(
        [
            "multisig",
            "perform-batch",
            "--contract",
            str(contract_address),
            "--abi",
            str(multisig_abi),
            "--batch",
            "7",
            "--pem",
            str(user),
            "--nonce",
            "0",
            "--gas-limit",
            "1000000",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == user_address
    assert tx["receiver"] == contract_address
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 1_000_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "performBatch@07"


def _read_stdout(capsys: Any) -> str:
    stdout: str = capsys.readouterr().out.strip()
    return stdout


def get_transaction(capsys: Any) -> dict[str, Any]:
    out = _read_stdout(capsys)
    output: dict[str, Any] = json.loads(out)
    return output["emittedTransaction"]
