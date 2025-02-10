import json
from pathlib import Path
from typing import Any

from multiversx_sdk_cli.cli import main

testdata_path = Path(__file__).parent / "testdata"
testdata_out = Path(__file__).parent / "testdata-out"


def test_create_tx_and_sign_by_hash(capsys: Any):
    return_code = main(
        [
            "tx",
            "new",
            "--pem",
            str(testdata_path / "alice.pem"),
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--nonce",
            "89",
            "--gas-limit",
            "50000",
            "--version",
            "2",
            "--options",
            "1",
            "--chain",
            "integration tests chain ID",
        ]
    )
    assert return_code == 0

    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)
    signature = tx_json["emittedTransaction"]["signature"]
    assert (
        signature
        == "f0c81f2393b1ec5972c813f817bae8daa00ade91c6f75ea604ab6a4d2797aca4378d783023ff98f1a02717fe4f24240cdfba0b674ee9abb18042203d713bc70a"
    )


def test_create_move_balance_transaction(capsys: Any):
    return_code = main(
        [
            "tx",
            "new",
            "--pem",
            str(testdata_path / "alice.pem"),
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--nonce",
            "215",
            "--gas-limit",
            "500000",
            "--value",
            "1000000000000",
            "--data",
            "hello",
            "--version",
            "2",
            "--options",
            "0",
            "--chain",
            "T",
        ]
    )
    assert return_code == 0
    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)
    signature = tx_json["emittedTransaction"]["signature"]
    assert (
        signature
        == "e88d846800bab1751e222c4461a310a3882312ef6d75fd8b861a2f3b572837b58f146ff9d60d16e617f53358d6cfa87cbcc65ad624c77003779d474059264901"
    )


def test_create_multi_transfer_transaction(capsys: Any):
    return_code = main(
        [
            "tx",
            "new",
            "--pem",
            str(testdata_path / "alice.pem"),
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--nonce",
            "212",
            "--gas-limit",
            "5000000",
            "--token-transfers",
            "SSSSS-941b91-01",
            "1",
            "TEST-738c3d",
            "1200000000",
            "--version",
            "2",
            "--options",
            "0",
            "--chain",
            "T",
        ]
    )
    assert return_code == 0
    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)
    signature = tx_json["emittedTransaction"]["signature"]
    assert (
        signature
        == "575b029d52ff5ffbfb7bab2f04052de88a6f7d022a6ad368459b8af9acaed3717d3f95db09f460649a8f405800838bc2c432496bd03c9039ea166bd32b84660e"
    )


def test_create_multi_transfer_transaction_with_single_egld_transfer(capsys: Any):
    return_code = main(
        [
            "tx",
            "new",
            "--pem",
            str(testdata_path / "alice.pem"),
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--nonce",
            "7",
            "--gas-limit",
            "1300000",
            "--token-transfers",
            "EGLD-000000",
            "1000000000000000000",
            "--chain",
            "T",
        ]
    )
    assert return_code == 0
    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)
    data = tx_json["emittedTransactionData"]
    assert (
        data
        == "MultiESDTNFTTransfer@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8@01@45474c442d303030303030@@0de0b6b3a7640000"
    )


def test_relayed_v3_without_relayer_wallet(capsys: Any):
    return_code = main(
        [
            "tx",
            "new",
            "--pem",
            str(testdata_path / "alice.pem"),
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--nonce",
            "7",
            "--gas-limit",
            "1300000",
            "--value",
            "1000000000000000000",
            "--chain",
            "T",
            "--relayer",
            "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5",
        ]
    )
    assert return_code == 0
    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)["emittedTransaction"]
    assert tx_json["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx_json["receiver"] == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
    assert tx_json["relayer"] == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
    assert tx_json["signature"]
    assert not tx_json["relayerSignature"]


def test_relayed_v3_incorrect_relayer():
    return_code = main(
        [
            "tx",
            "new",
            "--pem",
            str(testdata_path / "alice.pem"),
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--nonce",
            "7",
            "--gas-limit",
            "1300000",
            "--value",
            "1000000000000000000",
            "--chain",
            "T",
            "--relayer",
            "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5",
            "--relayer-pem",
            str(testdata_path / "alice.pem"),
        ]
    )
    assert return_code


def test_create_relayed_v3_transaction(capsys: Any):
    # create relayed v3 tx and save signature and relayer signature
    # create the same tx, save to file
    # sign from file with relayer wallet and make sure signatures match
    return_code = main(
        [
            "tx",
            "new",
            "--pem",
            str(testdata_path / "alice.pem"),
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--nonce",
            "7",
            "--gas-limit",
            "1300000",
            "--value",
            "1000000000000000000",
            "--chain",
            "T",
            "--relayer",
            "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5",
            "--relayer-pem",
            str(testdata_path / "testUser.pem"),
        ]
    )
    assert return_code == 0

    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)["emittedTransaction"]
    assert tx_json["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx_json["receiver"] == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
    assert tx_json["relayer"] == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
    assert tx_json["signature"]
    assert tx_json["relayerSignature"]

    initial_sender_signature = tx_json["signature"]
    initial_relayer_signature = tx_json["relayerSignature"]

    # Clear the captured content
    capsys.readouterr()

    # save tx to file then load and sign tx by relayer
    return_code = main(
        [
            "tx",
            "new",
            "--pem",
            str(testdata_path / "alice.pem"),
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--nonce",
            "7",
            "--gas-limit",
            "1300000",
            "--value",
            "1000000000000000000",
            "--chain",
            "T",
            "--relayer",
            "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5",
            "--outfile",
            str(testdata_out / "relayed.json"),
        ]
    )
    assert return_code == 0

    # Clear the captured content
    capsys.readouterr()

    return_code = main(
        [
            "tx",
            "relay",
            "--relayer-pem",
            str(testdata_path / "testUser.pem"),
            "--infile",
            str(testdata_out / "relayed.json"),
        ]
    )
    assert return_code == 0

    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)["emittedTransaction"]
    assert tx_json["signature"] == initial_sender_signature
    assert tx_json["relayerSignature"] == initial_relayer_signature

    # Clear the captured content
    capsys.readouterr()


def test_check_relayer_wallet_is_provided():
    return_code = main(["tx", "relay", "--infile", str(testdata_out / "relayed.json")])
    assert return_code


def test_create_plain_transaction(capsys: Any):
    return_code = main(
        [
            "tx",
            "new",
            "--pem",
            str(testdata_path / "alice.pem"),
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--nonce",
            "89",
            "--gas-limit",
            "50000",
            "--chain",
            "test",
        ]
    )
    assert return_code == 0

    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)["emittedTransaction"]

    assert tx_json["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx_json["receiver"] == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
    assert tx_json["chainID"] == "test"
    assert tx_json["gasLimit"] == 50000
    assert tx_json["version"] == 2
    assert tx_json["options"] == 0
    assert (
        tx_json["signature"]
        == "0cbb3cb4d6feaf9d2e6d17a529ddb5eeb0fd547af1dde65362beb6aaf54b78d90d429fa951b6ce7b52724be8da9737d7efaf13631816d034a2d7d1f5ae19510b"
    )


def _read_stdout(capsys: Any) -> str:
    return capsys.readouterr().out.strip()
