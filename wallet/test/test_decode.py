import unittest

from erdpy.wallet.keyfile import load_from_key_file, get_password


class TestDecode(unittest.TestCase):

    def test_decode(self):
        password = get_password("pass.txt")
        address, seed = load_from_key_file("keyfile.json", password)

        print(address)
        print(seed)
        print(password)

        self.assertEqual("1", "1")





