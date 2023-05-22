import json
from pathlib import Path
from multiversx_sdk_cli.cli import main


def test_sign_tx():
    parent = Path(__file__).parent
    unsigned_transaction = parent / "testdata" / "transaction.json"
    signed_transaction = parent / "testdata-out" / "signed_transaction.json"

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

    assert signed_tx["emittedTransaction"]["signature"]
