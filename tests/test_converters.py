import unittest

from erdpy.conv.conv import Converters


class ConvertersTestCase(unittest.TestCase):
    def test_str_to_hex_str(self):
        my_str = "1000000"
        hex_str = Converters.str_int_to_hex_str(my_str)
        self.assertEqual("0f4240", hex_str)

        my_str = "100000000000000000"
        hex_str = Converters.str_int_to_hex_str(my_str)
        self.assertEqual("00016345785d8a0000", hex_str)

    def test_parse_keys(self):
        keys = "myKey,newKey,anotherKey"
        parsed_keys, num_keys = Converters.parse_keys(keys)

        self.assertEqual(3, num_keys)
        self.assertEqual("@myKey@newKey@anotherKey", parsed_keys)


