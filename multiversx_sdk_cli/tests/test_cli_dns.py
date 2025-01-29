from pathlib import Path

from multiversx_sdk_cli.cli import main

testdata_path = Path(__file__).parent / "testdata"


def test_prepare_relayed_dns_register_transaction():
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

    assert False if return_code else True
