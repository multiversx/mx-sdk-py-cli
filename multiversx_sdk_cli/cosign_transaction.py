import requests
from multiversx_sdk import Transaction

from multiversx_sdk_cli.errors import GuardianServiceError


def cosign_transaction(transaction: Transaction, service_url: str, guardian_code: str):
    payload = {
        "code": f"{guardian_code}",
        "transactions": [transaction.to_dictionary()],
    }

    # we call sign-multiple-transactions to be allowed a bigger payload (e.g. deploying large contracts)
    url = f"{service_url}/sign-multiple-transactions"
    response = requests.post(url, json=payload)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise GuardianServiceError(f"Guardian service returned an error: {str(e)}")

    # we only send 1 transaction
    tx_as_dict = response.json()["data"]["transactions"][0]
    transaction.guardian_signature = bytes.fromhex(tx_as_dict["guardianSignature"])
