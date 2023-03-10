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
    displayed_mnemonic = capsys.readouterr().out.replace("Mnemonic:", "").strip()
    assert Mnemonic.is_text_valid(displayed_mnemonic)


def test_wallet_new_and_save_in_pem_format(capsys: Any):
    # Legacy invocation
    outfile = testdata_out_path / "testWallet.pem"
    outfile.unlink(missing_ok=True)
    main(["wallet", "new", "--pem", "--output-path", str(outfile)])

    mnemonic = Mnemonic(capsys.readouterr().out.replace("Mnemonic:", "").strip())
    expected_secret_key = mnemonic.derive_key(0)
    pem = UserPEM.from_file(outfile)
    assert pem.secret_key.hex() == expected_secret_key.hex()

    # New invocation
    outfile = testdata_out_path / "testWallet.pem"
    outfile.unlink(missing_ok=True)
    main(["wallet", "new", "--format", "pem", "--outfile", str(outfile)])

    mnemonic = Mnemonic(capsys.readouterr().out.replace("Mnemonic:", "").strip())
    expected_secret_key = mnemonic.derive_key(0)
    pem = UserPEM.from_file(outfile)
    assert pem.secret_key.hex() == expected_secret_key.hex()


def test_wallet_new_and_save_in_json_format(capsys: Any, monkeypatch: Any):
    # Legacy invocation
    outfile = testdata_out_path / "testWallet.json"
    outfile.unlink(missing_ok=True)
    monkeypatch.setattr(getpass, "getpass", lambda _: "password")
    main(["wallet", "new", "--json", "--output-path", str(outfile)])

    expected_mnemonic = Mnemonic(capsys.readouterr().out.replace("Mnemonic:", "").strip())
    keyfile = json.loads(outfile.read_text())
    mnemonic = UserWallet.decrypt_mnemonic(keyfile, "password")
    assert mnemonic.get_text() == expected_mnemonic.get_text()

    # New invocation
    outfile = testdata_out_path / "testWallet.json"
    outfile.unlink(missing_ok=True)
    monkeypatch.setattr(getpass, "getpass", lambda _: "password")
    main(["wallet", "new", "--format", "keystore-mnemonic", "--outfile", str(outfile)])

    expected_mnemonic = Mnemonic(capsys.readouterr().out.replace("Mnemonic:", "").strip())
    keyfile = json.loads(outfile.read_text())
    mnemonic = UserWallet.decrypt_mnemonic(keyfile, "password")
    assert mnemonic.get_text() == expected_mnemonic.get_text()


def test_wallet_derive_pem_from_mnemonic_deprecated(monkeypatch: Any):
    outfile = testdata_out_path / "wallet.pem"
    test_mnemonic = "moral volcano peasant pass circle pen over picture flat shop clap goat never lyrics gather prepare woman film husband gravity behind test tiger improve"
    monkeypatch.setattr("builtins.input", lambda _: test_mnemonic)

    main(["wallet", "derive", str(outfile), "--mnemonic"])

    expected_secret_key = Mnemonic(test_mnemonic).derive_key(0)
    pem = UserPEM.from_file(outfile)
    assert pem.secret_key.hex() == expected_secret_key.hex()


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
    monkeypatch.setattr(getpass, "getpass", lambda _: "password")

    main([
        "wallet", "new",
        "--format", "keystore-mnemonic",
        "--outfile", str(outfile)
    ])

    displayed_mnemonic = capsys.readouterr().out.replace("Mnemonic:", "").strip()
    keyfile = json.loads(outfile.read_text())
    mnemonic = UserWallet.decrypt_mnemonic(keyfile, "password")
    assert mnemonic.get_text() == displayed_mnemonic


def test_wallet_new_as_keystore_with_secret_key(capsys: Any, monkeypatch: Any):
    outfile = testdata_out_path / "keystore-with-mnemonic.json"
    outfile.unlink(missing_ok=True)
    monkeypatch.setattr(getpass, "getpass", lambda _: "password")

    main([
        "wallet", "new",
        "--format", "keystore-secret-key",
        "--outfile", str(outfile)
    ])

    displayed_mnemonic = Mnemonic(capsys.readouterr().out.replace("Mnemonic:", "").strip())
    expected_secret_key = displayed_mnemonic.derive_key(0)
    secret_key = UserWallet.load_secret_key(outfile, "password")
    assert secret_key.hex() == expected_secret_key.hex()


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
    monkeypatch.setattr(getpass, "getpass", lambda _: "password")

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
    monkeypatch.setattr(getpass, "getpass", lambda _: "password")

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
    monkeypatch.setattr(getpass, "getpass", lambda _: "password")

    main([
        "wallet", "convert",
        "--in-format", "keystore-secret-key", "--infile", str(infile),
        "--out-format", "pem", "--outfile", str(outfile)
    ])

    pem = UserPEM.from_file(outfile)
    assert pem.label == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert pem.secret_key.hex() == "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"
