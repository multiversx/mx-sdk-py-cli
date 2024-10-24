import requests
import time
import pytest

from pathlib import Path

from multiversx_sdk_cli.cli import main

testdata_path = Path(__file__).parent / "testdata"
testdata_out = Path(__file__).parent / "testdata-out"

proxy_url = "http://localhost:7950/network/config"
alice_pem = testdata_path / "alice.pem"
reward_address = "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"
bls_key = "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"


@pytest.fixture()
def poll_endpoint():
    start_time = time.time()  # Record the start time
    timeout = 60
    interval = 1

    while True:
        try:
            # Make the request to the endpoint
            response = requests.get(proxy_url, timeout=5)  # Add request timeout to prevent blocking indefinitely
            if response.status_code == 200:
                # Break out of the loop if we get a successful response
                return response.json()  # Return the response (or .text, .content based on your needs)
            else:
                print(f"Received non-200 status code: {response.status_code}")

        except requests.RequestException as e:
            # Handle network exceptions or timeouts
            print(f"Request failed: {e}")

        # Check if the timeout is reached
        if time.time() - start_time > timeout:
            print("Polling timed out")
            break

        # Wait for the specified interval before sending the next request
        time.sleep(interval)


@pytest.mark.require_localnet
def test_stake(poll_endpoint):
    validators_json = testdata_path / "validators.json"

    # Stake with recall nonce
    return_code = main([
        "validator", "stake",
        "--pem", str(alice_pem),
        "--value", "2500000000000000000000",
        "--validators-file", str(validators_json),
        "--reward-address", reward_address,
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0

    # Stake with provided nonce
    return_code = main([
        "validator", "stake",
        "--pem", str(alice_pem),
        "--value", "2500000000000000000000",
        "--validators-file", str(validators_json),
        "--reward-address", reward_address,
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--nonce=0"
    ])
    assert return_code == 0


@pytest.mark.require_localnet
def test_stake_top_up(poll_endpoint):
    # Stake with topUp
    return_code = main([
        "validator", "stake", "--top-up",
        "--pem", str(alice_pem),
        "--value", "2711000000000000000000",
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0


@pytest.mark.require_localnet
def test_unstake(poll_endpoint):
    # Unstake
    return_code = main([
        "validator", "unstake",
        "--pem", str(alice_pem),
        "--nodes-public-key", bls_key,
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0


@pytest.mark.require_localnet
def test_unbond(poll_endpoint):
    # Unbond
    return_code = main([
        "validator", "unbond",
        "--pem", str(alice_pem),
        "--nodes-public-key", bls_key,
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0


@pytest.mark.require_localnet
def test_unjail(poll_endpoint):
    # Unjail
    return_code = main([
        "validator", "unjail",
        "--pem", str(alice_pem),
        "--value", "2500000000000000000000",
        "--nodes-public-key", bls_key,
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0


@pytest.mark.require_localnet
def test_change_reward_address(poll_endpoint):
    # Change reward address
    return_code = main([
        "validator", "change-reward-address",
        "--pem", str(alice_pem),
        "--reward-address", reward_address,
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0


@pytest.mark.require_localnet
def test_unstake_nodes(poll_endpoint):
    # Unstake Nodes
    return_code = main([
        "validator", "unstake-nodes",
        "--pem", str(alice_pem),
        "--nodes-public-key", bls_key,
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0


@pytest.mark.require_localnet
def test_unstake_tokens(poll_endpoint):
    # Unstake Tokens
    return_code = main([
        "validator", "unstake-tokens",
        "--pem", str(alice_pem),
        "--unstake-value", "11000000000000000000",
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0


@pytest.mark.require_localnet
def test_unbond_nodes(poll_endpoint):
    # Unbond nodes
    return_code = main([
        "validator", "unbond-nodes",
        "--pem", str(alice_pem),
        "--nodes-public-keys", bls_key,
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0


@pytest.mark.require_localnet
def test_unbond_tokens(poll_endpoint):
    # Unbond nodes
    return_code = main([
        "validator", "unbond-tokens",
        "--pem", str(alice_pem),
        "--unbond-value", "20000000000000000000",
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0


@pytest.mark.require_localnet
def test_clean_registration_data(poll_endpoint):
    # Clean registration data
    return_code = main([
        "validator", "clean-registered-data",
        "--pem", str(alice_pem),
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0


@pytest.mark.require_localnet
def test_re_stake_unstaked_nodes(poll_endpoint):
    # Clean registration data
    return_code = main([
        "validator", "restake-unstaked-nodes",
        "--pem", str(alice_pem),
        "--nodes-public-keys", bls_key,
        "--chain", "localnet",
        "--proxy", "http://127.0.0.1:7950",
        "--estimate-gas", "--recall-nonce"
    ])
    assert return_code == 0
