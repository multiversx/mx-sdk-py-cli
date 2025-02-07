import json
from pathlib import Path
from typing import Any

from multiversx_sdk_cli.cli import main

testdata_path = Path(__file__).parent / "testdata"


def test_prepare_relayed_dns_register_transaction(capsys: Any):
    alice = testdata_path / "alice.pem"
    user = testdata_path / "testUser.pem"

    return_code = main(
        [
            "dns",
            "register",
            "--pem",
            str(alice),
            "--name",
            "alice.elrond",
            "--nonce",
            "0",
            "--gas-limit",
            "15000000",
            "--chain",
            "T",
            "--relayer",
            "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5",
            "--relayer-pem",
            str(user),
        ]
    )
    assert not return_code

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqpgqf97pgqdy0tstwauxu09kszz020hp5kgqqzzsscqtww"
    assert tx["value"] == "0"
    assert tx["nonce"] == 0
    assert tx["gasLimit"] == 15000000
    assert tx["chainID"] == "T"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert tx["relayer"] == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
    assert (
        tx["signature"]
        == "25af35896b853ad13bf1adcc3e516f8d7532349b4b00e958e30a6b9c0b9c38cbe0ce712684aba91e3f91bf080f6ae89d8cdfd6d0c69701d3761346aa6c54ac0d"
    )
    assert (
        tx["relayerSignature"]
        == "e7b22c3f8e3cfa8f15038d3b59beabe3e4b2a0e40fdb40e57c39e762450ebe3cdf327bb66585c27e66480846b7487d5e78366959f6f09f10bb63e9b643c08f03"
    )
    assert data == "register@616c6963652e656c726f6e64"


def get_output(capsys: Any):
    tx = _read_stdout(capsys)
    return json.loads(tx)


def _read_stdout(capsys: Any) -> str:
    return capsys.readouterr().out.strip()
