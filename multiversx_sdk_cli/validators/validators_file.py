import json
from pathlib import Path

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

    def _read_json_file_validators(self):
        val_file = self.validators_file_path.expanduser()
        guards.is_file(val_file)
        with open(self.validators_file_path, "r") as json_file:
            try:
                data = json.load(json_file)
            except Exception:
                raise CannotReadValidatorsData()
            return data
