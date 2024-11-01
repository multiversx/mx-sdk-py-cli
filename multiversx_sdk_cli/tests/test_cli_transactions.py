import json
from pathlib import Path
from typing import Any

from multiversx_sdk_cli.cli import main

testdata_path = Path(__file__).parent / "testdata"
testdata_out = Path(__file__).parent / "testdata-out"


def test_relayed_v1_transaction(capsys: Any):
    multi_user_pem = testdata_path / "multiple_addresses.pem"
    address_index = 1

    return_code = main([
        "tx", "new",
        "--pem", str(multi_user_pem),
        "--pem-index", str(address_index),
        "--receiver", "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
        "--nonce", "198",
        "--gas-limit", "60000000",
        "--data", "getContractConfig",
        "--version", "1",
        "--chain", "T",
        "--relay"
    ])
    assert return_code == 0

    relayed_tx = _read_stdout(capsys)
    assert relayed_tx == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414141415141414141414141414141414141414141414141414141414141432f2f383d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a2239682b6e6742584f5536776674315464437368534d4b3454446a5a32794f74686336564c576e3478724d5a706248427738677a6c6659596d362b766b505258303764634a562b4745635462616a7049692b5a5a5942773d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a317d"


def test_create_tx_and_sign_by_hash(capsys: Any):
    return_code = main([
        "tx", "new",
        "--pem", str(testdata_path / "alice.pem"),
        "--receiver", "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "--nonce", "89",
        "--gas-limit", "50000",
        "--version", "2",
        "--options", "1",
        "--chain", "integration tests chain ID",
    ])
    assert return_code == 0

    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)
    signature = tx_json["emittedTransaction"]["signature"]
    assert signature == "f0c81f2393b1ec5972c813f817bae8daa00ade91c6f75ea604ab6a4d2797aca4378d783023ff98f1a02717fe4f24240cdfba0b674ee9abb18042203d713bc70a"


def test_create_move_balance_transaction(capsys: Any):
    return_code = main([
        "tx", "new",
        "--pem", str(testdata_path / "alice.pem"),
        "--receiver", "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "--nonce", "215",
        "--gas-limit", "500000",
        "--value", "1000000000000",
        "--data", "hello",
        "--version", "2",
        "--options", "0",
        "--chain", "T",
    ])
    assert return_code == 0
    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)
    signature = tx_json["emittedTransaction"]["signature"]
    assert signature == "e88d846800bab1751e222c4461a310a3882312ef6d75fd8b861a2f3b572837b58f146ff9d60d16e617f53358d6cfa87cbcc65ad624c77003779d474059264901"


def test_create_multi_transfer_transaction(capsys: Any):
    return_code = main([
        "tx", "new",
        "--pem", str(testdata_path / "alice.pem"),
        "--receiver", "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "--nonce", "212",
        "--gas-limit", "5000000",
        "--token-transfers", "SSSSS-941b91-01", "1", "TEST-738c3d", "1200000000",
        "--version", "2",
        "--options", "0",
        "--chain", "T",
    ])
    assert return_code == 0
    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)
    signature = tx_json["emittedTransaction"]["signature"]
    assert signature == "575b029d52ff5ffbfb7bab2f04052de88a6f7d022a6ad368459b8af9acaed3717d3f95db09f460649a8f405800838bc2c432496bd03c9039ea166bd32b84660e"


def test_create_multi_transfer_transaction_with_single_egld_transfer(capsys: Any):
    return_code = main([
        "tx", "new",
        "--pem", str(testdata_path / "alice.pem"),
        "--receiver", "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "--nonce", "7",
        "--gas-limit", "1300000",
        "--token-transfers", "EGLD-000000", "1000000000000000000",
        "--chain", "T",
    ])
    assert return_code == 0
    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)
    data = tx_json["emittedTransactionData"]
    assert data == "MultiESDTNFTTransfer@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8@01@45474c442d303030303030@@0de0b6b3a7640000"


def _read_stdout(capsys: Any) -> str:
    return capsys.readouterr().out.strip()
