import unittest

from erdpy.validators.validators_file import ValidatorsFile


class ValidatorsFileTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.validators_file_path = "testdata/validators.json"

    def test_read_validators_files_num_of_nodes(self):
        validators_file = ValidatorsFile(self.validators_file_path)

        num_of_nodes = validators_file.get_num_of_nodes()
        self.assertEqual(3, num_of_nodes)

    def test_read_validators_files_get_validators_list(self):
        validators_file = ValidatorsFile(self.validators_file_path)

        validators_list = validators_file.get_validators_list()
        self.assertEqual(3, len(validators_list))
