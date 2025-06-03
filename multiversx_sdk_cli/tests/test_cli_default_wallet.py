import json
from pathlib import Path
from typing import Any

from multiversx_sdk_cli.cli import main


def test_empty_address_config(monkeypatch: Any, tmp_path: Path):
    test_file = tmp_path / "addresses.mxpy.json"
    test_file.write_text("{}")

    import multiversx_sdk_cli.address

    monkeypatch.setattr(multiversx_sdk_cli.address, "LOCAL_ADDRESS_CONFIG_PATH", test_file)
    multiversx_sdk_cli.address.read_address_config_file.cache_clear()

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
            "invalidSender",
        ]
    )
    assert return_code


def test_without_address_config(monkeypatch: Any, tmp_path: Path):
    test_file = tmp_path / "addresses.mxpy.json"
    assert not test_file.exists()

    import multiversx_sdk_cli.address

    monkeypatch.setattr(multiversx_sdk_cli.address, "LOCAL_ADDRESS_CONFIG_PATH", test_file)
    multiversx_sdk_cli.address.read_address_config_file.cache_clear()

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
            "invalidAlias",
        ]
    )
    assert return_code


def test_incomplete_address_config(monkeypatch: Any, tmp_path: Path):
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

    import multiversx_sdk_cli.address

    monkeypatch.setattr(multiversx_sdk_cli.address, "LOCAL_ADDRESS_CONFIG_PATH", test_file)
    multiversx_sdk_cli.address.read_address_config_file.cache_clear()

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

    import multiversx_sdk_cli.address

    monkeypatch.setattr(multiversx_sdk_cli.address, "LOCAL_ADDRESS_CONFIG_PATH", test_file)
    multiversx_sdk_cli.address.read_address_config_file.cache_clear()

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

    import multiversx_sdk_cli.address

    monkeypatch.setattr(multiversx_sdk_cli.address, "LOCAL_ADDRESS_CONFIG_PATH", test_file)
    multiversx_sdk_cli.address.read_address_config_file.cache_clear()

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
