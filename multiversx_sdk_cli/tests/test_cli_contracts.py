from pathlib import Path
from typing import Any

from multiversx_sdk_cli.cli import main

parent = Path(__file__).parent


def test_contract_build():
    main([
        "contract",
        "build",
        "--path",
        f"{parent}/testdata-out/SANDBOX/myadder-rs"
    ])

    assert Path.is_file(Path(f"{parent}/testdata-out/SANDBOX/myadder-rs/output/myadder-rs.wasm"))


def test_bad_contract_build(capsys: Any):
    ERROR = "Build error: error code = 101, see output."

    main([
        "contract",
        "build",
        "--path",
        f"{parent}/testdata-out/SANDBOX/myadder-rs-bad-src"
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
