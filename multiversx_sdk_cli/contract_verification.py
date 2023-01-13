import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Union
from multiversx_sdk_cli.accounts import Account, Address
from multiversx_sdk_cli.utils import read_json_file
from nacl.signing import SigningKey
import requests
from multiversx_sdk_rust_contract_builder.packaged_source_code import PackagedSourceCode


class ContractVerificationRequest:
    def __init__(
        self,
        contract: Address,
        source_code: Dict[str, Any],
        signature: bytes,
        docker_image: str,
    ) -> None:
        self.contract = contract
        self.source_code = source_code
        self.signature = signature
        self.docker_image = docker_image

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            "signature": self.signature.hex(),
            "payload": {
                "contract": self.contract.bech32(),
                "dockerImage": self.docker_image,
                "sourceCode": self.source_code
            }
        }


class ContractVerificationPayload:
    def __init__(self, contract: Address, source_code: Dict[str, Any], docker_image: str,) -> None:
        self.contract = contract
        self.source_code = source_code
        self.docker_image = docker_image

    def serialize(self):
        payload = {
            "contract": self.contract.bech32(),
            "dockerImage": self.docker_image,
            "sourceCode": self.source_code
        }

        return json.dumps(payload, separators=(',', ':'))


def trigger_contract_verification(
    packaged_source: Union[Path, None],
    project_directory: Union[Path, None],
    owner: Account,
    contract: Address,
    verifier_url: str,
    docker_image: str,
):
    if packaged_source:
        source_code = read_json_file(packaged_source)
        source_code = PackagedSourceCode.from_dict(source_code).to_dict()
    elif project_directory:
        source_code = PackagedSourceCode.from_folder(project_directory).to_dict()
    else:
        raise NotImplementedError()

    payload = ContractVerificationPayload(contract, source_code, docker_image).serialize()

    hashed_payload = hashlib.sha256(payload.encode()).hexdigest()

    secret_key = bytes.fromhex(owner.secret_key)
    signing_key: Any = SigningKey(secret_key)

    message = f"{contract.bech32()}{hashed_payload}"

    signed_message = signing_key.sign(message.encode())
    signature = signed_message.signature

    contract_verification = ContractVerificationRequest(contract, source_code, signature, docker_image)

    request_dictionary = contract_verification.to_dictionary()
    response = requests.post(verifier_url, json=request_dictionary)

    return response
