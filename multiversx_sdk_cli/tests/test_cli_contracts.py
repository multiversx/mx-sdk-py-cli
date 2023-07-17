from pathlib import Path

from multiversx_sdk_cli.cli import main


def test_contract_deploy():
    parent = Path(__file__).parent
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
    parent = Path(__file__).parent
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
    parent = Path(__file__).parent
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
