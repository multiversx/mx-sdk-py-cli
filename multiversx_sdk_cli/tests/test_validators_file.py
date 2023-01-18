import unittest
from pathlib import Path

from multiversx_sdk_cli.validators.validators_file import ValidatorsFile


class ValidatorsFileTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.testdata = Path(__file__).parent.joinpath("testdata")
        self.validators_file_path = self.testdata / "validators.json"

    def test_read_validators_files_num_of_nodes(self):
        validators_file = ValidatorsFile(self.validators_file_path)

        num_of_nodes = validators_file.get_num_of_nodes()
        self.assertEqual(3, num_of_nodes)

    def test_read_validators_files_get_validators_list(self):
        validators_file = ValidatorsFile(self.validators_file_path)

        validators_list = validators_file.get_validators_list()
        self.assertEqual(3, len(validators_list))
