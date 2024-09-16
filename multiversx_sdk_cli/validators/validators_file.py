import json
from pathlib import Path
from typing import Dict, List

from multiversx_sdk import ValidatorPEM, ValidatorPublicKey, ValidatorSigner

from multiversx_sdk_cli import guards
from multiversx_sdk_cli.errors import CannotReadValidatorsData


class ValidatorsFile:
    def __init__(self, validators_file_path: Path):
        self.validators_file_path = validators_file_path
        self._validators_data = self._read_json_file_validators()

    def get_num_of_nodes(self) -> int:
        return len(self._validators_data.get("validators", []))

    def get_validators_list(self):
        return self._validators_data.get("validators", [])

    def load_signers(self) -> List[ValidatorSigner]:
        signers: List[ValidatorSigner] = []
        for validator in self.get_validators_list():
            pem_file = self._load_validator_pem(validator)
            validator_signer = ValidatorSigner(pem_file.secret_key)
            signers.append(validator_signer)

        return signers

    def load_public_keys(self) -> List[ValidatorPublicKey]:
        public_keys: List[ValidatorPublicKey] = []

        for validator in self.get_validators_list():
            pem_file = self._load_validator_pem(validator)
            public_keys.append(pem_file.secret_key.generate_public_key())

        return public_keys

    def _load_validator_pem(self, validator: Dict[str, str]) -> ValidatorPEM:
        # Get path of "pemFile", make it absolute
        validator_pem = Path(validator.get("pemFile", "")).expanduser()
        validator_pem = validator_pem if validator_pem.is_absolute() else self.validators_file_path.parent / validator_pem

        return ValidatorPEM.from_file(validator_pem)

    def _read_json_file_validators(self):
        val_file = self.validators_file_path.expanduser()
        guards.is_file(val_file)
        with open(self.validators_file_path, "r") as json_file:
            try:
                data = json.load(json_file)
            except Exception:
                raise CannotReadValidatorsData()
            return data
