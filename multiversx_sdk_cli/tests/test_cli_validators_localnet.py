from pathlib import Path

import pytest

from multiversx_sdk_cli.cli import main

testdata_path = Path(__file__).parent / "testdata"

alice_pem = testdata_path / "alice.pem"
reward_address = "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"
bls_key = "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"


@pytest.mark.require_localnet
def test_stake():
    validators_json = testdata_path / "validators_ci.pem"

    # Stake with recall nonce
    return_code = main(
        [
            "validator",
            "stake",
            "--pem",
            str(alice_pem),
            "--value",
            "2500000000000000000000",
            "--validators-pem",
            str(validators_json),
            "--reward-address",
            reward_address,
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0

    # Stake with provided nonce
    return_code = main(
        [
            "validator",
            "stake",
            "--pem",
            str(alice_pem),
            "--value",
            "2500000000000000000000",
            "--validators-pem",
            str(validators_json),
            "--reward-address",
            reward_address,
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--nonce=0",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0


@pytest.mark.require_localnet
def test_stake_top_up():
    # Stake with topUp
    return_code = main(
        [
            "validator",
            "stake",
            "--top-up",
            "--pem",
            str(alice_pem),
            "--value",
            "2711000000000000000000",
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0


@pytest.mark.require_localnet
def test_unstake():
    # Unstake
    return_code = main(
        [
            "validator",
            "unstake",
            "--pem",
            str(alice_pem),
            "--nodes-public-key",
            bls_key,
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0


@pytest.mark.require_localnet
def test_unbond():
    # Unbond
    return_code = main(
        [
            "validator",
            "unbond",
            "--pem",
            str(alice_pem),
            "--nodes-public-key",
            bls_key,
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0


@pytest.mark.require_localnet
def test_unjail():
    # Unjail
    return_code = main(
        [
            "validator",
            "unjail",
            "--pem",
            str(alice_pem),
            "--value",
            "2500000000000000000000",
            "--nodes-public-key",
            bls_key,
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0


@pytest.mark.require_localnet
def test_change_reward_address():
    # Change reward address
    return_code = main(
        [
            "validator",
            "change-reward-address",
            "--pem",
            str(alice_pem),
            "--reward-address",
            reward_address,
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0


@pytest.mark.require_localnet
def test_unstake_nodes():
    # Unstake Nodes
    return_code = main(
        [
            "validator",
            "unstake-nodes",
            "--pem",
            str(alice_pem),
            "--nodes-public-key",
            bls_key,
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0


@pytest.mark.require_localnet
def test_unstake_tokens():
    # Unstake Tokens
    return_code = main(
        [
            "validator",
            "unstake-tokens",
            "--pem",
            str(alice_pem),
            "--unstake-value",
            "11000000000000000000",
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0


@pytest.mark.require_localnet
def test_unbond_nodes():
    # Unbond nodes
    return_code = main(
        [
            "validator",
            "unbond-nodes",
            "--pem",
            str(alice_pem),
            "--nodes-public-keys",
            bls_key,
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0


@pytest.mark.require_localnet
def test_unbond_tokens():
    # Unbond nodes
    return_code = main(
        [
            "validator",
            "unbond-tokens",
            "--pem",
            str(alice_pem),
            "--unbond-value",
            "20000000000000000000",
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0


@pytest.mark.require_localnet
def test_clean_registration_data():
    # Clean registration data
    return_code = main(
        [
            "validator",
            "clean-registered-data",
            "--pem",
            str(alice_pem),
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0


@pytest.mark.require_localnet
def test_re_stake_unstaked_nodes():
    # Clean registration data
    return_code = main(
        [
            "validator",
            "restake-unstaked-nodes",
            "--pem",
            str(alice_pem),
            "--nodes-public-keys",
            bls_key,
            "--chain",
            "localnet",
            "--proxy",
            "http://127.0.0.1:7950",
            "--gas-limit",
            "60000000",
        ]
    )
    assert return_code == 0
