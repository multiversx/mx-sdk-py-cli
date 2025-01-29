from typing import Any

from multiversx_sdk import Transaction
import requests

from multiversx_sdk_cli.errors import GuardianServiceError


def cosign_transaction(transaction: Transaction, service_url: str, guardian_code: str) -> Transaction:
    payload = {
        "code": f"{guardian_code}",
        "transactions": [transaction.to_dictionary()]
    }

    # we call sign-multiple-transactions to be allowed a bigger payload (e.g. deploying large contracts)
    url = f"{service_url}/sign-multiple-transactions"
    response = requests.post(url, json=payload)
    check_for_guardian_error(response.json())

    # we only send 1 transaction
    tx_as_dict = response.json()["data"]["transactions"][0]
    transaction.guardian_signature = bytes.fromhex(tx_as_dict["guardianSignature"])

    return transaction


def check_for_guardian_error(response: dict[str, Any]):
    error = response["error"]

    if error:
        raise GuardianServiceError(error)
