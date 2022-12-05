from pathlib import Path
from typing import Dict, Any, Union
from erdpy.accounts import Account, Address
from erdpy.utils import read_json_file
from nacl.signing import SigningKey
import requests


class ContractVerificationRequest:
    def __init__(
        self,
        contract: Address,
        source_code: Dict[str, Any],
        signature: Any,
        docker_tag: str,
    ) -> None:
        self.contract = contract
        self.source_code = source_code
        self.signature = signature
        self.docker_tag = docker_tag

    def to_dictionary(self) -> Dict[str, Any]:
        contract_verification_request: Dict[str, Any] = {}

        contract_verification_request["contract"] = self.contract
        contract_verification_request["source_code"] = self.source_code
        contract_verification_request["signature"] = self.signature
        contract_verification_request["docker_tag"] = self.docker_tag

        return contract_verification_request


def trigger_contract_verification(
    packaged_source: Union[Path, None],
    project_directory: Union[Path, None],
    owner: Account,
    contract: Address,
    verifier_url: str,
    docker_tag: str,
) -> None:
    if packaged_source:
        source_code = read_json_file(packaged_source)
    elif project_directory:
        raise NotImplementedError()

    secret_key = bytes.fromhex(owner.secret_key)
    signing_key: Any = SigningKey(secret_key)

    message = f"{contract.bech32()} some dummy string"
    signed_message = signing_key.sign(message.encode())
    signature = signed_message.signature

    contract_verification = ContractVerificationRequest(
        contract, source_code, signature, docker_tag
    )

    request = requests.post(verifier_url, data=contract_verification.to_dictionary())
