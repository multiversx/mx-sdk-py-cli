from pathlib import Path

import pytest

from multiversx_sdk_cli.cli import main

from .shared import CHAIN_ID, SANDBOX, TestUser, TestUser2, clean_sandbox

testdata_path = Path(__file__).parent / "testdata"
REGISTRATION_COST = "100"


@pytest.fixture(autouse=True)
def run_before_tests():
    clean_sandbox()


def test_prepare_relayed_dns_register_transaction():
    alice = testdata_path / "alice.pem"

    return_code = main([
        "dns", "register",
        "--pem", str(alice),
        "--name", "alice.elrond",
        "--nonce", "0",
        "--gas-limit", "15000000",
        "--chain", "T",
        "--relay"
    ])

    assert False if return_code else True


def test_registration_offline():
    return_code = main([
        "dns", "register",
        "--name", "testuser.elrond",
        "--pem", str(TestUser),
        "--value", REGISTRATION_COST,
        "--nonce", "7",
        "--gas-limit", "100000000",
        "--chain", CHAIN_ID,
        "--outfile", str(SANDBOX / "txRegisterUser.txt")
    ])
    assert not return_code
    assert (SANDBOX / "txRegisterUser.txt").is_file()

    return_code = main([
        "dns", "register",
        "--name", "testuser2.elrond",
        "--pem", str(TestUser2),
        "--value", REGISTRATION_COST,
        "--nonce", "8",
        "--gas-limit", "100000000",
        "--chain", CHAIN_ID,
        "--outfile", str(SANDBOX / "txRegisterUser2.txt")
    ])
    assert not return_code
    assert (SANDBOX / "txRegisterUser2.txt").is_file()
