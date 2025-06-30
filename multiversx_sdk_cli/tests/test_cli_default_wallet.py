import json
from pathlib import Path
from typing import Any

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.cli import main


def test_empty_wallet_config(capsys: Any, monkeypatch: Any, tmp_path: Path):
    test_file = tmp_path / "wallets.mxpy.json"
    test_file.write_text("{}")

    import multiversx_sdk_cli.config_wallet

    monkeypatch.setattr(multiversx_sdk_cli.config_wallet, "LOCAL_WALLET_CONFIG_PATH", test_file)
    monkeypatch.setattr(multiversx_sdk_cli.config_wallet, "GLOBAL_WALLET_CONFIG_PATH", test_file)
    multiversx_sdk_cli.config_wallet.read_wallet_config_file.cache_clear()

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    out = _read_stdout(capsys)
    assert return_code
    assert "No wallet provided." in out

    # Clear the captured content
    capsys.readouterr()

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
            "--sender",
            "invalidSender",
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert return_code
    out = _read_stdout(capsys)
    assert "Wallet config file is empty." in out


def test_without_address_config(capsys: Any, monkeypatch: Any, tmp_path: Path):
    # Ensure the address config file does not exist; if the actual name is used, when running the tests locally, it will fail with a different error message
    test_file = tmp_path / "test-wallets.mxpy.json"
    assert not test_file.exists()

    import multiversx_sdk_cli.config_wallet

    monkeypatch.setattr(multiversx_sdk_cli.config_wallet, "LOCAL_WALLET_CONFIG_PATH", test_file)
    monkeypatch.setattr(multiversx_sdk_cli.config_wallet, "GLOBAL_WALLET_CONFIG_PATH", test_file)
    multiversx_sdk_cli.config_wallet.read_wallet_config_file.cache_clear()

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert return_code
    out = _read_stdout(capsys)
    assert "No wallet provided." in out

    # Clear the captured content
    capsys.readouterr()

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
            "--sender",
            "invalidAlias",
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert return_code
    out = _read_stdout(capsys)
    assert "The wallet config file was not found." in out


def test_incomplete_address_config(capsys: Any, monkeypatch: Any, tmp_path: Path):
    test_file = tmp_path / "wallets.mxpy.json"
    import multiversx_sdk_cli.config_wallet

    json_file = {
        "active": "alice",
        "wallets": {
            "alice": {
                "index": "0",
            },
        },
    }
    test_file.write_text(json.dumps(json_file))

    monkeypatch.setattr(multiversx_sdk_cli.config_wallet, "LOCAL_WALLET_CONFIG_PATH", test_file)
    monkeypatch.setattr(multiversx_sdk_cli.config_wallet, "GLOBAL_WALLET_CONFIG_PATH", test_file)
    multiversx_sdk_cli.config_wallet.read_wallet_config_file.cache_clear()

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert return_code
    out = _read_stdout(capsys)
    assert "'path' field must be set in the wallet config." in out

    # Clear the captured content
    capsys.readouterr()

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
            "--sender",
            "alice",
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert return_code
    out = _read_stdout(capsys)
    assert "'path' field must be set in the wallet config." in out

    # Clear the captured content
    capsys.readouterr()

    json_file = {
        "active": "alice",
        "wallets": {
            "alice": {
                "kind": "keystore",
                "path": "/example/to/wallet.json",
                "index": "0",
            },
        },
    }
    test_file.write_text(json.dumps(json_file))

    monkeypatch.setattr(multiversx_sdk_cli.config_wallet, "LOCAL_WALLET_CONFIG_PATH", test_file)
    multiversx_sdk_cli.config_wallet.read_wallet_config_file.cache_clear()

    monkeypatch.setattr(cli_shared, "getpass", lambda *args, **kwargs: "")

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert return_code

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
            "--sender",
            "alice",
            "--nonce",
            "0",
            "--chain",
            "D",
        ]
    )
    assert return_code


def _read_stdout(capsys: Any) -> str:
    stdout: str = capsys.readouterr().out.strip()
    return stdout
