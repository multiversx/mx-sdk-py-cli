import json
import os
from pathlib import Path
from typing import Any, List

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


def test_create_and_save_inner_transaction():
    return_code = main([
        "tx", "new",
        "--pem", str(testdata_path / "alice.pem"),
        "--receiver", "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "--nonce", "77",
        "--gas-limit", "500000",
        "--relayer", "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8",
        "--inner-transactions-outfile", str(testdata_out / "inner_transactions.json"),
        "--chain", "T",
    ])
    assert False if return_code else True
    assert Path(testdata_out / "inner_transactions.json").is_file()


def test_create_and_append_inner_transaction():
    return_code = main([
        "tx", "new",
        "--pem", str(testdata_path / "alice.pem"),
        "--receiver", "erd1fggp5ru0jhcjrp5rjqyqrnvhr3sz3v2e0fm3ktknvlg7mcyan54qzccnan",
        "--nonce", "1234",
        "--gas-limit", "50000",
        "--relayer", "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8",
        "--inner-transactions-outfile", str(testdata_out / "inner_transactions.json"),
        "--chain", "T",
    ])
    assert False if return_code else True

    with open(testdata_out / "inner_transactions.json", "r") as file:
        json_file = json.load(file)

    inner_txs: List[Any] = json_file["innerTransactions"]
    assert len(inner_txs) == 2


def test_create_invalid_relayed_transaction():
    return_code = main([
        "tx", "new",
        "--pem", str(testdata_path / "testUser.pem"),
        "--receiver", "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5",
        "--nonce", "987",
        "--gas-limit", "5000000",
        "--inner-transactions", str(testdata_out / "inner_transactions.json"),
        "--data", "test data",
        "--chain", "T",
    ])
    assert return_code


def test_create_relayer_transaction(capsys: Any):
    return_code = main([
        "tx", "new",
        "--pem", str(testdata_path / "testUser.pem"),
        "--receiver", "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5",
        "--nonce", "987",
        "--gas-limit", "5000000",
        "--inner-transactions", str(testdata_out / "inner_transactions.json"),
        "--chain", "T",
    ])
    # remove test file to ensure consistency when running test file locally
    os.remove(testdata_out / "inner_transactions.json")

    assert False if return_code else True

    tx = _read_stdout(capsys)
    tx_json = json.loads(tx)["emittedTransaction"]

    assert tx_json["sender"] == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
    assert tx_json["receiver"] == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
    assert tx_json["gasLimit"] == 5000000
    assert tx_json["nonce"] == 987
    assert tx_json["chainID"] == "T"

    # should be the two inner transactions created in the tests above
    inner_transactions = tx_json["innerTransactions"]
    assert len(inner_transactions) == 2

    assert inner_transactions[0]["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert inner_transactions[0]["receiver"] == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
    assert inner_transactions[0]["nonce"] == 77
    assert inner_transactions[0]["relayer"] == "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"

    assert inner_transactions[1]["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert inner_transactions[1]["receiver"] == "erd1fggp5ru0jhcjrp5rjqyqrnvhr3sz3v2e0fm3ktknvlg7mcyan54qzccnan"
    assert inner_transactions[1]["nonce"] == 1234
    assert inner_transactions[1]["relayer"] == "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"


def _read_stdout(capsys: Any) -> str:
    return capsys.readouterr().out.strip()
