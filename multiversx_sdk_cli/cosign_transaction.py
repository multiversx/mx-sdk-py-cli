import requests
from typing import Dict, Any, Protocol
from multiversx_sdk_cli.errors import GuardianServiceError


class ITransaction(Protocol):
    guardianSignature: str

    def to_dictionary(self) -> Dict[str, Any]:
        ...


def cosign_transaction(transaction: ITransaction, service_url: str, guardian_code: str) -> ITransaction:
    payload = {
        "code": f"{guardian_code}",
        "transaction": transaction.to_dictionary()
    }

    url = f"{service_url}/sign-transaction"
    response = requests.post(url, json=payload)
    check_for_guardian_error(response.json())

    tx_as_dict = response.json()["data"]["transaction"]
    transaction.guardianSignature = tx_as_dict["guardianSignature"]

    return transaction


def check_for_guardian_error(response: Dict[str, Any]):
    error = response["error"]

    if error:
        raise GuardianServiceError(error)
