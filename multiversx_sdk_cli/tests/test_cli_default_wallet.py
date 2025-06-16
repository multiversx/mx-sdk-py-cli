import json
from pathlib import Path
from typing import Any

from multiversx_sdk_cli.cli import main


def test_empty_address_config(capsys: Any, monkeypatch: Any, tmp_path: Path):
    test_file = tmp_path / "addresses.mxpy.json"
    test_file.write_text("{}")

    import multiversx_sdk_cli.address_config

    monkeypatch.setattr(multiversx_sdk_cli.address_config, "LOCAL_ADDRESS_CONFIG_PATH", test_file)
    multiversx_sdk_cli.address_config.read_address_config_file.cache_clear()

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
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
        ]
    )
    assert return_code
    out = _read_stdout(capsys)
    assert "Address config file is empty." in out


def test_without_address_config(capsys: Any, monkeypatch: Any, tmp_path: Path):
    test_file = tmp_path / "addresses.mxpy.json"
    assert not test_file.exists()

    import multiversx_sdk_cli.address_config

    monkeypatch.setattr(multiversx_sdk_cli.address_config, "LOCAL_ADDRESS_CONFIG_PATH", test_file)
    multiversx_sdk_cli.address_config.read_address_config_file.cache_clear()

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
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
        ]
    )
    assert return_code
    out = _read_stdout(capsys)
    assert "Alias is not known: invalidAlias." in out


def test_incomplete_address_config(capsys: Any, monkeypatch: Any, tmp_path: Path):
    test_file = tmp_path / "addresses.mxpy.json"
    json_file = {
        "active": "alice",
        "addresses": {
            "alice": {
                "path": "/example/to/wallet.pem",
                "index": "0",
            },
        },
    }
    test_file.write_text(json.dumps(json_file))

    import multiversx_sdk_cli.address_config

    monkeypatch.setattr(multiversx_sdk_cli.address_config, "LOCAL_ADDRESS_CONFIG_PATH", test_file)
    multiversx_sdk_cli.address_config.read_address_config_file.cache_clear()

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
        ]
    )
    assert return_code
    out = _read_stdout(capsys)
    assert "'kind' field must be set in the address config." in out

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
        ]
    )
    assert return_code
    out = _read_stdout(capsys)
    assert "'kind' field must be set in the address config." in out

    # Clear the captured content
    capsys.readouterr()

    json_file = {
        "active": "alice",
        "addresses": {
            "alice": {
                "kind": "pem",
                "index": "0",
            },
        },
    }
    test_file.write_text(json.dumps(json_file))

    monkeypatch.setattr(multiversx_sdk_cli.address_config, "LOCAL_ADDRESS_CONFIG_PATH", test_file)
    multiversx_sdk_cli.address_config.read_address_config_file.cache_clear()

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
        ]
    )
    assert return_code
    out = _read_stdout(capsys)
    assert "'path' field must be set in the address config." in out

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
        ]
    )
    assert return_code
    out = _read_stdout(capsys)
    assert "'path' field must be set in the address config." in out

    # Clear the captured content
    capsys.readouterr()

    json_file = {
        "active": "alice",
        "addresses": {
            "alice": {
                "kind": "keystore",
                "path": "/example/to/wallet.json",
                "index": "0",
            },
        },
    }
    test_file.write_text(json.dumps(json_file))

    monkeypatch.setattr(multiversx_sdk_cli.address_config, "LOCAL_ADDRESS_CONFIG_PATH", test_file)
    multiversx_sdk_cli.address_config.read_address_config_file.cache_clear()

    return_code = main(
        [
            "tx",
            "new",
            "--receiver",
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "--gas-limit",
            "50000",
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
        ]
    )
    assert return_code


def _read_stdout(capsys: Any) -> str:
    stdout: str = capsys.readouterr().out.strip()
    return stdout
