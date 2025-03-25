import json
from pathlib import Path
from typing import Any

from multiversx_sdk import ValidatorPEM

from multiversx_sdk_cli.cli import main

testdata_path = Path(__file__).parent / "testdata"
testdata_out_path = Path(__file__).parent / "testdata-out"


def test_create_validator_wallet():
    outfile = testdata_out_path / "validator.pem"
    outfile.unlink(missing_ok=True)

    return_code = main(
        [
            "validator-wallet",
            "new",
            "--outfile",
            str(outfile),
        ]
    )
    assert not return_code
    assert outfile.is_file()

    wallet = ValidatorPEM.from_file(outfile)
    assert wallet.label
    assert wallet.secret_key


def test_validator_sign_and_verify_message(capsys: Any):
    message = "test"
    validator = testdata_path / "validator_01.pem"

    return_code = main(
        [
            "validator-wallet",
            "sign-message",
            "--message",
            message,
            "--pem",
            str(validator),
        ]
    )
    assert not return_code

    out = json.loads(_read_stdout(capsys))
    assert out == {
        "address": "f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d",
        "message": "test",
        "signature": "0x1c1dc0f6ef4f7c2a335cabd1da4bf3f333902c90ad9ecff0873854453419cd092f490238fb2f1bc6bf9f89337dea188f",
    }

    # Clear the captured content
    capsys.readouterr()

    return_code = main(
        [
            "validator-wallet",
            "verify-message-signature",
            "--pubkey",
            "f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d",
            "--message",
            message,
            "--signature",
            "0x1c1dc0f6ef4f7c2a335cabd1da4bf3f333902c90ad9ecff0873854453419cd092f490238fb2f1bc6bf9f89337dea188f",
        ]
    )
    assert not return_code
    out = _read_stdout(capsys)

    success = "SUCCESS:"
    assert success in out.split()

    # repeate signature check with invalid signature
    # Clear the captured content
    capsys.readouterr()

    return_code = main(
        [
            "validator-wallet",
            "verify-message-signature",
            "--pubkey",
            "f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d",
            "--message",
            message,
            "--signature",
            "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        ]
    )
    assert not return_code
    out = _read_stdout(capsys)

    success = "SUCCESS:"
    assert success not in out.split()

    fail = "FAILED:"
    assert fail in out.split()


def test_validator_wallet_convert_to_hex_secret_key(capsys: Any):
    infile = testdata_path / "validator_01.pem"

    return_code = main(
        [
            "validator-wallet",
            "convert",
            "--infile",
            str(infile),
        ]
    )
    assert not return_code

    output = _read_stdout(capsys)
    lines = output.splitlines()

    assert (
        lines[0]
        == "Public key: f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d"
    )
    assert lines[1] == "Secret key: 7c19bf3a0c57cdd1fb08e4607cebaa3647d6b9261b4693f61e96e54b218d442a"


def _read_stdout(capsys: Any) -> str:
    stdout: str = capsys.readouterr().out.strip()
    return stdout
