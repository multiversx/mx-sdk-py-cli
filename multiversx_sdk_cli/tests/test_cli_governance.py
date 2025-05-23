import base64
import json
from pathlib import Path
from typing import Any

from multiversx_sdk_cli.cli import main

testdata = Path(__file__).parent / "testdata"
alice = testdata / "alice.pem"
alice_address = "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
governance_contract = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqrlllsrujgla"
commit_hash = "1db734c0315f9ec422b88f679ccfe3e0197b9d67"


def test_new_proposal(capsys: Any):
    return_code = main(
        [
            "governance",
            "propose",
            "--commit-hash",
            commit_hash,
            "--start-vote-epoch",
            "10",
            "--end-vote-epoch",
            "15",
            "--value",
            "1000000000000000000000",
            "--pem",
            str(alice),
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == alice_address
    assert tx["receiver"] == governance_contract
    assert tx["value"] == "1000000000000000000000"
    assert tx["gasLimit"] == 50_192_500
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == f"proposal@{commit_hash.encode().hex()}@0a@0f"


def test_vote(capsys: Any):
    return_code = main(
        [
            "governance",
            "vote",
            "--proposal-nonce",
            "1",
            "--vote",
            "yes",
            "--pem",
            str(alice),
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == alice_address
    assert tx["receiver"] == governance_contract
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 5_171_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "vote@01@796573"


def test_close_proposal(capsys: Any):
    return_code = main(
        [
            "governance",
            "close-proposal",
            "--proposal-nonce",
            "1",
            "--pem",
            str(alice),
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == alice_address
    assert tx["receiver"] == governance_contract
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 50_074_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "closeProposal@01"


def test_clear_ended_proposals(capsys: Any):
    return_code = main(
        [
            "governance",
            "clear-ended-proposals",
            "--proposers",
            alice_address,
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--pem",
            str(alice),
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == alice_address
    assert tx["receiver"] == governance_contract
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 150_273_500
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert (
        data
        == "clearEndedProposals@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
    )


def test_claim_accumulated_fees(capsys: Any):
    return_code = main(
        [
            "governance",
            "claim-accumulated-fees",
            "--pem",
            str(alice),
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == alice_address
    assert tx["receiver"] == governance_contract
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 1_080_000
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert data == "claimAccumulatedFees"


def test_change_config(capsys: Any):
    return_code = main(
        [
            "governance",
            "change-config",
            "--proposal-fee",
            "1000000000000000000000",
            "--lost-proposal-fee",
            "10000000000000000000",
            "--min-quorum",
            "5000",
            "--min-veto-threshold",
            "3000",
            "--min-pass-threshold",
            "6000",
            "--pem",
            str(alice),
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert not return_code
    tx = get_transaction(capsys)

    assert tx["sender"] == alice_address
    assert tx["receiver"] == governance_contract
    assert tx["value"] == "0"
    assert tx["gasLimit"] == 50_237_500
    assert tx["chainID"] == "D"
    data = tx["data"]
    data = base64.b64decode(data).decode()
    assert (
        data
        == "changeConfig@31303030303030303030303030303030303030303030@3130303030303030303030303030303030303030@35303030@33303030@36303030"
    )


def _read_stdout(capsys: Any) -> str:
    stdout: str = capsys.readouterr().out.strip()
    return stdout


def get_transaction(capsys: Any) -> dict[str, Any]:
    out = _read_stdout(capsys)
    output: dict[str, Any] = json.loads(out)
    return output["emittedTransaction"]
