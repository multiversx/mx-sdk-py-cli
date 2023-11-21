import json
from pathlib import Path
from typing import Any

import pytest

from multiversx_sdk_cli.cli import main

parent = Path(__file__).parent


def test_contract_new():
    main([
        "contract",
        "new",
        "--template",
        "adder",
        "--path",
        f"{parent}/testdata-out/SANDBOX"
    ])
    assert Path.is_dir(parent / "testdata-out" / "SANDBOX" / "adder")


def test_contract_new_with_bad_code():
    # we change the contract code so the build would fail so we can catch the error
    main([
        "contract",
        "new",
        "--template",
        "adder",
        "--path",
        f"{parent}/testdata-out/SANDBOX",
        "--name",
        "adder-bad-src"
    ])

    assert Path.is_dir(parent / "testdata-out" / "SANDBOX" / "adder-bad-src")
    replace_variable_with_unknown_variable_for_adder()


def replace_variable_with_unknown_variable_for_adder():
    # this is done in order to replace the value added in the adder contract with a unknown variable
    with open(parent / "testdata-out" / "SANDBOX" / "adder-bad-src" / "src" / "adder_bad_src.rs", "r") as f:
        contract_lines = f.readlines()

    for index, line in reversed(list(enumerate(contract_lines))):
        if "value" in line:
            contract_lines[index] = line.replace("value", "unknown_variable")
            break

    with open(parent / "testdata-out" / "SANDBOX" / "adder-bad-src" / "src" / "adder_bad_src.rs", "w") as f:
        f.writelines(contract_lines)


@pytest.mark.skip_on_windows
def test_contract_build():
    main([
        "contract",
        "build",
        "--path",
        f"{parent}/testdata-out/SANDBOX/adder"
    ])

    assert Path.is_file(parent / "testdata-out" / "SANDBOX" / "adder" / "output" / "adder.wasm")


@pytest.mark.skip_on_windows
def test_bad_contract_build(capsys: Any):
    ERROR = "Build error: error code = 101, see output."

    main([
        "contract",
        "build",
        "--path",
        f"{parent}/testdata-out/SANDBOX/adder-bad-src"
    ])

    out, _ = capsys.readouterr()

    if ERROR in out:
        assert True
    else:
        assert False


def test_contract_deploy():
    output_file = parent / "testdata-out" / "deploy.json"

    main(
        [
            "contract",
            "deploy",
            "--bytecode",
            f"{parent}/testdata/adder.wasm",
            "--pem",
            f"{parent}/testdata/testUser.pem",
            "--proxy",
            "https://testnet-api.multiversx.com",
            "--chain",
            "T",
            "--recall-nonce",
            "--gas-limit",
            "5000000",
            "--arguments",
            "0",
            "--outfile",
            str(output_file),
        ]
    )
    assert Path.is_file(output_file) == True


def test_contract_upgrade():
    output_file = parent / "testdata-out" / "upgrade.json"
    contract_address = "erd1qqqqqqqqqqqqqpgq5l9jl0j0gnqmm7hn82zaydwux3s5xuwkyq8srt5vsy"

    main(
        [
            "contract",
            "upgrade",
            contract_address,
            "--bytecode",
            f"{parent}/testdata/adder.wasm",
            "--pem",
            f"{parent}/testdata/testUser.pem",
            "--proxy",
            "https://testnet-api.multiversx.com",
            "--chain",
            "T",
            "--recall-nonce",
            "--gas-limit",
            "5000000",
            "--arguments",
            "0",
            "--outfile",
            str(output_file),
        ]
    )
    assert Path.is_file(output_file) == True


def test_contract_call():
    output_file = parent / "testdata-out" / "call.json"
    contract_address = "erd1qqqqqqqqqqqqqpgq5l9jl0j0gnqmm7hn82zaydwux3s5xuwkyq8srt5vsy"

    main(
        [
            "contract",
            "call",
            contract_address,
            "--function",
            "add",
            "--pem",
            f"{parent}/testdata/testUser.pem",
            "--proxy",
            "https://testnet-api.multiversx.com",
            "--chain",
            "T",
            "--recall-nonce",
            "--gas-limit",
            "5000000",
            "--arguments",
            "5",
            "--outfile",
            str(output_file),
        ]
    )
    assert Path.is_file(output_file) == True


def test_contract_flow(capsys: Any):
    alice = f"{parent}/testdata/alice.pem"
    adder = f"{parent}/testdata/adder.wasm"

    main([
        "contract", "deploy",
        "--bytecode", adder,
        "--pem", alice,
        "--recall-nonce",
        "--gas-limit", "5000000",
        "--proxy", "https://testnet-api.multiversx.com",
        "--arguments", "0",
        "--send", "--wait-result"
    ])
    contract = get_contract_address(capsys)

    # Clear the captured content
    capsys.readouterr()

    main([
        "contract", "query",
        contract,
        "--function", "getSum",
        "--proxy", "https://testnet-api.multiversx.com"
    ])
    response = get_query_response(capsys)
    assert response == ""

    # Clear the captured content
    capsys.readouterr()

    main([
        "contract", "call",
        contract,
        "--pem", alice,
        "--function", "add",
        "--recall-nonce",
        "--gas-limit", "5000000",
        "--proxy", "https://testnet-api.multiversx.com",
        "--arguments", "7",
        "--send", "--wait-result"
    ])

    # Clear the captured content
    capsys.readouterr()

    main([
        "contract", "query",
        contract,
        "--function", "getSum",
        "--proxy", "https://testnet-api.multiversx.com"
    ])
    response = get_query_response(capsys)
    assert response["number"] == 7

    # Clear the captured content
    capsys.readouterr()

    main([
        "contract", "upgrade",
        contract,
        "--bytecode", adder,
        "--pem", alice,
        "--recall-nonce",
        "--gas-limit", "5000000",
        "--proxy", "https://testnet-api.multiversx.com",
        "--arguments", "0",
        "--send", "--wait-result"
    ])


def _read_stdout(capsys: Any) -> str:
    return capsys.readouterr().out.strip()


def get_contract_address(capsys: Any):
    out = _read_stdout(capsys)
    output = json.loads(out)
    return output["contractAddress"]


def get_query_response(capsys: Any):
    out = _read_stdout(capsys).replace("\n", "").replace(" ", "")
    print(out)
    return json.loads(out)[0]
