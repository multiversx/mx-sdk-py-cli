import json
from pathlib import Path
from multiversx_sdk_cli.cli import main


def test_create_and_save_transaction():
    parent = Path(__file__).parent
    output_file = parent / "testdata-out" / "signed_tx.json"

    main([
        "tx",
        "new",
        "--pem",
        f"{parent}/testdata/testUser.pem",
        "--receiver",
        "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        "--chain",
        "T",
        "--proxy",
        "https://testnet-api.multiversx.com",
        "--nonce",
        "7",
        "--data",
        "test transaction",
        "--gas-limit",
        "74000",
        "--value",
        "1000000000000000000",
        "--outfile",
        f"{output_file}"
    ])

    assert Path.is_file(output_file) == True


def test_modify_transaction():
    parent = Path(__file__).parent
    infile = parent / "testdata-out" / "signed_tx.json"
    outfile = parent / "testdata-out" / "modified_tx.json"

    with open(infile) as f:
        transaction = json.load(f)

    transaction["emittedTransaction"]["nonce"] = 777

    with open(outfile, "w") as f:
        f.write(json.dumps(transaction, indent=4))

    assert Path.is_file(outfile)


def test_sign_modified_tx():
    parent = Path(__file__).parent
    initial_tx_json = parent / "testdata-out" / "signed_tx.json"
    modified_tx_json = parent / "testdata-out" / "modified_tx.json"
    resigned_tx_json = parent / "testdata-out" / "signed_modified_tx.json"

    main([
        "tx",
        "sign",
        "--pem",
        f"{parent}/testdata/testUser.pem",
        "--infile",
        f"{modified_tx_json}",
        "--outfile",
        f"{resigned_tx_json}"
    ])

    with open(initial_tx_json) as f:
        initial_tx = json.load(f)

    with open(resigned_tx_json) as f:
        resigned_tx = json.load(f)

    assert initial_tx["emittedTransaction"]["signature"] != resigned_tx["emittedTransaction"]["signature"]
