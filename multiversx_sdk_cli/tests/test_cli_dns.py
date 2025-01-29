from pathlib import Path

from multiversx_sdk_cli.cli import main

testdata_path = Path(__file__).parent / "testdata"


def test_prepare_relayed_dns_register_transaction():
    alice = testdata_path / "alice.pem"

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
            "--relay",
        ]
    )

    assert False if return_code else True
