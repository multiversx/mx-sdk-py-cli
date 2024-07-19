import json
from pathlib import Path

from multiversx_sdk_cli.cli import main


def test_sign_tx():
    parent = Path(__file__).parent
    unsigned_transaction = parent / "testdata" / "transaction.json"
    signed_transaction = parent / "testdata-out" / "signed_transaction.json"
    expected_signature = "7b0fa3bd477a9aacdfd8d6b41628e525afbbc94b4b56c2a30a10f78514c2f6558b27eef701633481f1ef54b62697c91e9dc06cc6d2038bd13cf9557467142005"

    main([
        "tx",
        "sign",
        "--pem",
        f"{parent}/testdata/testUser.pem",
        "--infile",
        f"{unsigned_transaction}",
        "--outfile",
        f"{signed_transaction}"
    ])

    with open(signed_transaction) as f:
        signed_tx = json.load(f)

    assert signed_tx["emittedTransaction"]["signature"] == expected_signature
