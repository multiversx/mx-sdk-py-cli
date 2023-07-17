from pathlib import Path

from multiversx_sdk_cli.validators.validators_file import ValidatorsFile


class ValidatorsFileTestCase:
    testdata = Path(__file__).parent.joinpath("testdata")
    validators_file_path = testdata / "validators.json"

    def test_read_validators_files_num_of_nodes(self):
        validators_file = ValidatorsFile(self.validators_file_path)

        num_of_nodes = validators_file.get_num_of_nodes()
        assert num_of_nodes == 3

    def test_read_validators_files_get_validators_list(self):
        validators_file = ValidatorsFile(self.validators_file_path)

        validators_list = validators_file.get_validators_list()
        assert len(validators_list) == 3
