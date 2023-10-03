import getpass
import json
from pathlib import Path
from typing import Any

from multiversx_sdk_wallet import Mnemonic, UserPEM, UserWallet

from multiversx_sdk_cli.cli import main

testdata_path = Path(__file__).parent / "testdata"
testdata_out_path = Path(__file__).parent / "testdata-out"


def test_wallet_new(capsys: Any):
    main(["wallet", "new"])
    displayed_mnemonic = _read_stdout_mnemonic(capsys)
    assert Mnemonic.is_text_valid(displayed_mnemonic)


def test_wallet_new_and_save_in_pem_format(capsys: Any):
    outfile = testdata_out_path / "testWallet.pem"
    outfile.unlink(missing_ok=True)
    main(["wallet", "new", "--format", "pem", "--outfile", str(outfile)])

    expected_secret_key = Mnemonic(_read_stdout_mnemonic(capsys)).derive_key(0)
    actual_secret_key = UserPEM.from_file(outfile).secret_key
    assert actual_secret_key.hex() == expected_secret_key.hex()


def test_wallet_new_and_save_in_json_format(capsys: Any, monkeypatch: Any):
    outfile = testdata_out_path / "testWallet.json"
    outfile.unlink(missing_ok=True)
    _mock_getpass(monkeypatch, "password")
    main(["wallet", "new", "--format", "keystore-mnemonic", "--outfile", str(outfile)])

    expected_mnemonic = Mnemonic(_read_stdout_mnemonic(capsys))
    keyfile = json.loads(outfile.read_text())
    actual_mnemonic = UserWallet.decrypt_mnemonic(keyfile, "password")
    assert actual_mnemonic.get_text() == expected_mnemonic.get_text()


def test_wallet_new_as_mnemonic():
    outfile = testdata_out_path / "wallet.txt"
    outfile.unlink(missing_ok=True)

    main([
        "wallet", "new",
        "--format", "raw-mnemonic",
        "--outfile", str(outfile)
    ])

    assert Mnemonic.is_text_valid(outfile.read_text())


def test_wallet_new_as_pem():
    outfile = testdata_out_path / "wallet.pem"
    outfile.unlink(missing_ok=True)

    main([
        "wallet", "new",
        "--format", "pem",
        "--outfile", str(outfile),
        "--address-hrp", "erd"
    ])

    assert UserPEM.from_file(outfile).label.startswith("erd1")

    outfile.unlink(missing_ok=True)

    main([
        "wallet", "new",
        "--format", "pem",
        "--outfile", str(outfile),
        "--address-hrp", "test"
    ])

    assert UserPEM.from_file(outfile).label.startswith("test1")


def test_wallet_new_as_keystore_with_mnemonic(capsys: Any, monkeypatch: Any):
    outfile = testdata_out_path / "keystore-with-mnemonic.json"
    outfile.unlink(missing_ok=True)
    _mock_getpass(monkeypatch, "password")

    main([
        "wallet", "new",
        "--format", "keystore-mnemonic",
        "--outfile", str(outfile)
    ])

    expected_mnemonic = _read_stdout_mnemonic(capsys)
    keyfile = json.loads(outfile.read_text())
    actual_mnemonic = UserWallet.decrypt_mnemonic(keyfile, "password")
    assert actual_mnemonic.get_text() == expected_mnemonic


def test_wallet_new_as_keystore_with_secret_key(capsys: Any, monkeypatch: Any):
    outfile = testdata_out_path / "keystore-with-mnemonic.json"
    outfile.unlink(missing_ok=True)
    _mock_getpass(monkeypatch, "password")

    main([
        "wallet", "new",
        "--format", "keystore-secret-key",
        "--outfile", str(outfile)
    ])

    expected_secret_key = Mnemonic(_read_stdout_mnemonic(capsys)).derive_key(0)
    actual_secret_key = UserWallet.load_secret_key(outfile, "password")
    assert actual_secret_key.hex() == expected_secret_key.hex()


def test_wallet_convert_raw_mnemonic_to_pem():
    infile = testdata_path / "mnemonic.txt"
    outfile = testdata_out_path / "alice.pem"
    outfile.unlink(missing_ok=True)

    main([
        "wallet", "convert",
        "--in-format", "raw-mnemonic", "--infile", str(infile),
        "--out-format", "pem", "--outfile", str(outfile),
        "--address-index", "0"
    ])

    pem = UserPEM.from_file(outfile)
    assert pem.label == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert pem.secret_key.hex() == "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"


def test_wallet_convert_raw_mnemonic_to_keystore_with_mnemonic(monkeypatch: Any):
    infile = testdata_path / "mnemonic.txt"
    outfile = testdata_out_path / "keystore_with_mnemonic.json"

    outfile.unlink(missing_ok=True)
    _mock_getpass(monkeypatch, "password")

    main([
        "wallet", "convert",
        "--in-format", "raw-mnemonic", "--infile", str(infile),
        "--out-format", "keystore-mnemonic", "--outfile", str(outfile)
    ])

    keyfile_json = outfile.read_text()
    keyfile = json.loads(keyfile_json)
    mnemonic = UserWallet.decrypt_mnemonic(keyfile, "password")
    assert mnemonic.get_text() == infile.read_text()


def test_wallet_convert_raw_mnemonic_to_keystore_with_secret_key(monkeypatch: Any):
    infile = testdata_path / "mnemonic.txt"
    outfile = testdata_out_path / "keystore_with_secret_key.json"

    # Alice
    outfile.unlink(missing_ok=True)
    _mock_getpass(monkeypatch, "password")

    main([
        "wallet", "convert",
        "--in-format", "raw-mnemonic", "--infile", str(infile),
        "--out-format", "keystore-secret-key", "--outfile", str(outfile),
        "--address-index", "0"
    ])

    keyfile_json = outfile.read_text()
    keyfile = json.loads(keyfile_json)
    secret_key = UserWallet.decrypt_secret_key(keyfile, "password")
    assert secret_key.hex() == "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"

    # Bob
    outfile.unlink(missing_ok=True)
    main([
        "wallet", "convert",
        "--in-format", "raw-mnemonic", "--infile", str(infile),
        "--out-format", "keystore-secret-key", "--outfile", str(outfile),
        "--address-index", "1"
    ])

    keyfile_json = outfile.read_text()
    keyfile = json.loads(keyfile_json)
    secret_key = UserWallet.decrypt_secret_key(keyfile, "password")
    assert secret_key.hex() == "b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639"


def test_wallet_convert_keystore_with_secret_key_to_pem(monkeypatch: Any):
    infile = testdata_path / "alice.json"
    outfile = testdata_out_path / "alice.pem"

    outfile.unlink(missing_ok=True)
    _mock_getpass(monkeypatch, "password")

    main([
        "wallet", "convert",
        "--in-format", "keystore-secret-key", "--infile", str(infile),
        "--out-format", "pem", "--outfile", str(outfile)
    ])

    pem = UserPEM.from_file(outfile)
    assert pem.label == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert pem.secret_key.hex() == "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"


def test_wallet_bech32_encode(capsys: Any):
    main([
        "wallet", "bech32", "--encode", "0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    ])

    out = _read_stdout(capsys)
    assert out == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"


def test_wallet_bech32_decode(capsys: Any):
    main([
        "wallet", "bech32", "--decode", "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    ])

    out = _read_stdout(capsys)
    assert out == "0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"


def test_wallet_convert_pem_to_bech32_address(capsys: Any):
    infile = testdata_path / "alice.pem"

    main([
        "wallet", "convert", "--infile", str(infile), "--in-format", "pem", "--out-format", "address-bech32"
    ])

    out = _read_stdout(capsys).strip("Output:\n\n")
    assert out == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"


def test_wallet_convert_pem_to_pubkey(capsys: Any):
    infile = testdata_path / "alice.pem"

    main([
        "wallet", "convert", "--infile", str(infile), "--in-format", "pem", "--out-format", "address-hex"
    ])

    out = _read_stdout(capsys).strip("Output:\n\n")
    assert out == "0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"


def test_wallet_sign_message(capsys: Any):
    message = "test"
    pem = testdata_path / "alice.pem"

    return_code = main(["wallet", "sign-message", "--message", message, "--pem", str(pem)])
    out = json.loads(_read_stdout(capsys))

    assert False if return_code else True
    assert out == {
        "address": "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        "message": "test",
        "signature": "0x7aff43cd6e3d880a65033bf0a1b16274854fd7dfa9fe5faa7fa9a665ee851afd4c449310f5f1697d348e42d1819eaef69080e33e7652d7393521ed50d7427a0e"
    }


def test_verify_previously_signed_message(capsys: Any):
    message = "test"
    address = "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    signature = "0x7aff43cd6e3d880a65033bf0a1b16274854fd7dfa9fe5faa7fa9a665ee851afd4c449310f5f1697d348e42d1819eaef69080e33e7652d7393521ed50d7427a0e"

    return_code = main([
        "wallet",
        "verify-message",
        "--bech32-address",
        address,
        "--message",
        message,
        "--signature",
        signature
    ])
    out = _read_stdout(capsys)

    assert False if return_code else True
    assert """The message "test" was signed by erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th""" in out


def test_verify_not_signed_message(capsys: Any):
    message = "this message is not signed"
    address = "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    signature = "0x7aff43cd6e3d880a65033bf0a1b16274854fd7dfa9fe5faa7fa9a665ee851afd4c449310f5f1697d348e42d1819eaef69080e33e7652d7393521ed50d7427a0e"

    return_code = main([
        "wallet",
        "verify-message",
        "--bech32-address",
        address,
        "--message",
        message,
        "--signature",
        signature
    ])
    out = _read_stdout(capsys)

    assert False if return_code else True
    assert """The message "this message is not signed" was NOT signed by erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th""" in out


def _read_stdout_mnemonic(capsys: Any) -> str:
    return _read_stdout(capsys).replace("Mnemonic:", "").strip()


def _read_stdout(capsys: Any) -> str:
    return capsys.readouterr().out.strip()


def _mock_getpass(monkeypatch: Any, password: str):
    monkeypatch.setattr(getpass, "getpass", lambda _: password)
