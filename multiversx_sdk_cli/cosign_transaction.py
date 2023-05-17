import requests
from typing import Dict, Any, Protocol
from multiversx_sdk_cli.errors import GuardianServiceError


class ITransaction(Protocol):
    guardian_signature: str

    def to_dictionary(self) -> Dict[str, Any]:
        ...


def cosign_transaction(transaction: ITransaction, service_url: str, guardian_code: str) -> ITransaction:
    payload = compute_payload(transaction, guardian_code)
    url = f"{service_url}/sign-transaction"
    response = requests.post(url, json=payload)
    check_for_guardian_error(response.json())

    tx_as_dict = response.json()["data"]["transaction"]
    transaction.guardian_signature = tx_as_dict["guardianSignature"]

    return transaction


def compute_payload(transaction: ITransaction, guardian_code: str) -> Dict[str, Any]:
    return {
        "code": f"{guardian_code}",
        "transaction": transaction.to_dictionary()
    }


def check_for_guardian_error(response: Dict[str, Any]):
    error = response["error"]

    if error:
        raise GuardianServiceError(error)
