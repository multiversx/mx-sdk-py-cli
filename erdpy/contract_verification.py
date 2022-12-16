from pathlib import Path
from typing import Dict, Any, Union
from erdpy.accounts import Account, Address
from erdpy.utils import read_json_file
from nacl.signing import SigningKey
import requests
from build_contract_rust.packaged_source_code import PackagedSourceCode


class ContractVerificationRequest:
    def __init__(
        self,
        contract: Address,
        source_code: Dict[str, Any],
        signature: Any,
        docker_image: str,
    ) -> None:
        self.contract = contract
        self.source_code = source_code
        self.signature = signature
        self.docker_image = docker_image

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            "contract": self.contract,
            "source_code": self.source_code,
            "signature": self.signature,
            "docker_tag": self.docker_image
        }


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

    secret_key = bytes.fromhex(owner.secret_key)
    signing_key: Any = SigningKey(secret_key)

    token = get_verification_token(verifier_url, contract)

    message = f"{contract.bech32()}-{token}"
    signed_message = signing_key.sign(message.encode())
    signature = signed_message.signature

    contract_verification = ContractVerificationRequest(
        contract, source_code, signature, docker_image
    )

    response = requests.post(f'{verifier_url}/verify', data=contract_verification.to_dictionary())

    return response


def get_verification_token(verifier_url: str, contract: Address) -> str:
    response = requests.post(f"{verifier_url}/initialize", data={"contract": contract.bech32()})
    response.raise_for_status()
    response = response.json()
    token = str(response.get("token", ""))

    return token
