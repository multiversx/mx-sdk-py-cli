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


def test_propose_egld_transfer(capsys: Any):
    return_code = main([
        "tx", "new",
        "--pem", str(alice),
        "--receiver", "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "--nonce", "1429",
        "--chain", "T",
        "--gas-limit", "10000000",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--value", "1000000000000000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeTransferExecute@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8@038d7ea4c68000"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0

    signature = transaction["signature"]
    assert signature == "285edffe65006f738ce6fff640ddd9cb69c7380a219ec3549cb35744cd1106ffd41005b8d471899eb1db55e556b042db7bab0830a5250860348fb101d644c805"


def test_propose_esdt_transfer(capsys: Any):
    return_code = main([
        "tx", "new",
        "--pem", str(alice),
        "--receiver", "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "--nonce", "1427",
        "--chain", "T",
        "--gas-limit", "10000000",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--token-transfers", "TST-267761", "10"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeAsyncCall@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8@00@455344545472616e73666572@5453542d323637373631@0a"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0

    signature = transaction["signature"]
    assert signature == "dc80e70409fce3a20bd5c80ef1f1039a0474729ddb27188afacbd2d8237294172d5bf8b4bc759e48a2e5c724983dbb6ba5f17b48bb7a8d2dfc4c076a113fa50f"


def test_propose_multi_esdt_nft_transfer(capsys: Any):
    return_code = main([
        "tx", "new",
        "--pem", str(alice),
        "--receiver", "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "--nonce", "1434",
        "--chain", "T",
        "--gas-limit", "10000000",
        "--multisig", "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30",
        "--token-transfers", "TST-267761", "10", "ZZZ-9ee87d", "10000"
    ])
    assert False if return_code else True

    transaction = get_transaction(capsys)

    data_field: str = transaction["data"]
    data = base64.b64decode(data_field.encode()).decode()
    assert data == "proposeAsyncCall@000000000000000005000a2a0f13340978c2eea268a5a2dcf917012978f61f5c@00@4d756c7469455344544e46545472616e73666572@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8@02@5453542d323637373631@@0a@5a5a5a2d396565383764@@2710"

    receiver = transaction["receiver"]
    assert receiver == "erd1qqqqqqqqqqqqqpgqpg4q7ye5p9uv9m4zdzj69h8ezuqjj78krawq9zqz30"

    chain_id = transaction["chainID"]
    assert chain_id == "T"

    value = int(transaction["value"])
    assert value == 0

    signature = transaction["signature"]
    assert signature == "563fc6eefe9469cf90191462cfe21ab25ae7291c1c411cd4b3778717c827045eabc58b689308e8ee45676a8e49cf75c2856a83e41e93dad5c4acb5ccb65c5b04"


def get_transaction(capsys: Any) -> Dict[str, Any]:
    out = _read_stdout(capsys)
    output = json.loads(out)
    return output["emittedTransaction"]


def _read_stdout(capsys: Any) -> str:
    return capsys.readouterr().out.strip()
