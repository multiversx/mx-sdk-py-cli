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
        "--directory",
        f"{parent}/testdata-out/SANDBOX",
        "adder"
    ])
    assert Path.is_dir(parent / "testdata-out" / "SANDBOX" / "adder")


def test_contract_new_with_bad_code():
    # we change the contract code so the build would fail so we can catch the error
    main([
        "contract",
        "new",
        "--template",
        "adder",
        "--directory",
        f"{parent}/testdata-out/SANDBOX",
        "adder-bad-src"
    ])

    assert Path.is_dir(parent / "testdata-out" / "SANDBOX" / "adder-bad-src")
    replace_variable_with_unknown_variable()


def replace_variable_with_unknown_variable():
    # this is done in order to replace the value added in the adder contract with a unknown variable
    with open(parent / "testdata-out" / "SANDBOX" / "adder-bad-src" / "src" / "adder.rs", "r") as f:
        contract_lines = f.readlines()

    for index, line in reversed(list(enumerate(contract_lines))):
        if "value" in line:
            contract_lines[index] = line.replace("value", "unknown_variable")
            break

    with open(parent / "testdata-out" / "SANDBOX" / "adder-bad-src" / "src" / "adder.rs", "w") as f:
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
