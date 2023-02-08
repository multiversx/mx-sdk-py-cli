import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Tuple

import requests
from multiversx_sdk_core import MessageV1
from nacl.signing import SigningKey

from multiversx_sdk_cli.accounts import Account, Address
from multiversx_sdk_cli.errors import KnownError
from multiversx_sdk_cli.utils import dump_out_json, read_json_file

HTTP_REQUEST_TIMEOUT = 408
HTTP_SUCCESS = 200

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
    signature = _create_request_signature(owner, contract, payload.encode())
    contract_verification = ContractVerificationRequest(contract, source_code, signature, docker_image)

    request_dictionary = contract_verification.to_dictionary()

    url = f"{verifier_url}/verifier"
    status_code, message, data = _do_post(url, request_dictionary)

    if status_code == HTTP_REQUEST_TIMEOUT:
        task_id = data.get("taskId", "")

        if task_id:
            query_status_with_task_id(verifier_url, task_id)
        else:
            dump_out_json(data)
    elif status_code != HTTP_SUCCESS:
        dump_out_json(data)
        raise KnownError(f"Cannot verify contract: {message}")
    else:
        status = data.get("status", "")
        if status:
            logger.info(f"Task status: {status}")
            dump_out_json(data)
        else:
            task_id = data.get("taskId", "")
            query_status_with_task_id(verifier_url, task_id)


def _create_request_signature(account: Account, contract_address: Address, request_payload: bytes) -> bytes:
    secret_key = bytes.fromhex(account.secret_key)
    signing_key: Any = SigningKey(secret_key)

    hashed_payload: str = hashlib.sha256(request_payload).hexdigest()
    raw_data_to_sign = f"{contract_address.bech32()}{hashed_payload}"
    message_to_sign = MessageV1(raw_data_to_sign.encode())
    message_data_to_sign: bytes = message_to_sign.serialize_for_signing()
    signed_message = signing_key.sign(message_data_to_sign)
    signature: bytes = signed_message.signature

    logger.info(f"raw_data_to_sign = {raw_data_to_sign}, message_data_to_sign = {message_data_to_sign.hex()}, signature = {signature.hex()}")

    return signature


def query_status_with_task_id(url: str, task_id: str, interval: int = 10):
    logger.info(f"Please wait while we verify your contract. This may take a while.")
    old_status = ""

    while True:
        _, _, response = _do_get(f"{url}/tasks/{task_id}")
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


def _do_post(url: str, payload: Any) -> Tuple[int, str, Dict[str, Any]]:
    logger.debug(f"_do_post() to {url}")
    response = requests.post(url, json=payload)

    try:
        data = response.json()
        message = data.get("message", "")
        return response.status_code, message, data
    except Exception as error:
        logger.error(f"Erroneous response from {url}: {response.text}")
        raise KnownError(f"Cannot parse response from {url}", error)


def _do_get(url: str) -> Tuple[int, str, Dict[str, Any]]:
    logger.debug(f"_do_get() from {url}")
    response = requests.get(url)

    try:
        data = response.json()
        message = data.get("message", "")
        return response.status_code, message, data
    except Exception as error:
        logger.error(f"Erroneous response from {url}: {response.text}")
        raise KnownError(f"Cannot parse response from {url}", error)
