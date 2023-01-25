import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any

from multiversx_sdk_cli.utils import dump_out_json
from multiversx_sdk_cli.accounts import Account, Address
from multiversx_sdk_cli.utils import read_json_file
from nacl.signing import SigningKey
import requests

logger = logging.getLogger("cli.contracts.verifier")

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
    packaged_source: Path,
    owner: Account,
    contract: Address,
    verifier_url: str,
    docker_image: str,
):
    source_code = read_json_file(packaged_source)

    payload = ContractVerificationPayload(contract, source_code, docker_image).serialize()

    hashed_payload = hashlib.sha256(payload.encode()).hexdigest()

    secret_key = bytes.fromhex(owner.secret_key)
    signing_key: Any = SigningKey(secret_key)

    message = f"{contract.bech32()}{hashed_payload}"

    signed_message = signing_key.sign(message.encode())
    signature = signed_message.signature

    contract_verification = ContractVerificationRequest(contract, source_code, signature, docker_image)

    request_dictionary = contract_verification.to_dictionary()

    url = f"{verifier_url}/verifier"
    response = requests.post(url, json=request_dictionary).json()

    status = response.get("status", "")
    if status:
        logger.info(f"Task status: {status}")

        if status == "error":
            dump_out_json(response)
        else:
            dump_out_json(response)
    else:
        task_id = response.get("taskId", "")
        query_status_with_task_id(verifier_url, task_id)


def query_status_with_task_id(url: str, task_id: str, interval: int = 10):
    logger.info(f"Please wait while we verify your contract. This may take a while.")
    old_status = ""

    while True:
        response = requests.get(f"{url}/tasks/{task_id}").json()
        status = response.get("status", "")

        if status == "finished":
            logger.info(f"Verification finished!")
            dump_out_json(response)
            break
        elif status != old_status:
            logger.info(f"Task status: {status}")
            dump_out_json(response)
            old_status = status
        
        time.sleep(interval)
