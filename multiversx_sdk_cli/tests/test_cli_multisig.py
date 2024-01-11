import base64
import json
from pathlib import Path
from typing import Any, Dict

from multiversx_sdk_cli.cli import main

parent = Path(__file__).parent
alice = parent / "testdata" / "alice.pem"


def test_sign_action(capsys: Any):
    return_code = main([
        "multisig", "sign",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--action-id", "2",
        "--pem", str(alice),
        "--nonce", "1289",
        "--gas-limit", "10000000",
        "--proxy", "https://testnet-api.multiversx.com"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "sign@02"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"


def test_perform_action(capsys: Any):
    return_code = main([
        "multisig", "perform-action",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--action-id", "2",
        "--pem", str(alice),
        "--nonce", "1290",
        "--gas-limit", "10000000",
        "--proxy", "https://testnet-api.multiversx.com"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "performAction@02"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"


def get_transaction(capsys: Any) -> Dict[str, Any]:
    out = _read_stdout(capsys)
    output = json.loads(out)
    return output["emittedTransaction"]


def _read_stdout(capsys: Any) -> str:
    return capsys.readouterr().out.strip()
