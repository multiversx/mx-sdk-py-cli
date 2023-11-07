from typing import Any, Dict

import requests

from multiversx_sdk_cli.errors import GuardianServiceError
from multiversx_sdk_cli.interfaces import ITransaction


def cosign_transaction(transaction: ITransaction, service_url: str, guardian_code: str) -> ITransaction:
    payload = {
        "code": f"{guardian_code}",
        "transaction": transaction.__dict__
    }

    url = f"{service_url}/sign-transaction"
    response = requests.post(url, json=payload)
    check_for_guardian_error(response.json())

    tx_as_dict = response.json()["data"]["transaction"]
    transaction.guardian_signature = bytes.fromhex(tx_as_dict["guardianSignature"])

    return transaction


def check_for_guardian_error(response: Dict[str, Any]):
    error = response["error"]

    if error:
        raise GuardianServiceError(error)
