import unittest

from erdpy.wallet.keyfile import load_from_key_file, get_password


class TestDecode(unittest.TestCase):

    def test_decode(self):
        password = get_password("testdata/keys/pass.txt")
        address, seed = load_from_key_file("testdata/keys"
                                           "/erd1cps3p86d0rkluvx6n2l2j2xudy9dgdk4qtjf3pjpga8s5748nezqpxtsdd.json",
                                           password)

        self.assertEqual(seed.hex(), "b3708c10153a762cbc95cc370f296840c74d160731536fd26fe97953f637a220")
        self.assertEqual("erd1cps3p86d0rkluvx6n2l2j2xudy9dgdk4qtjf3pjpga8s5748nezqpxtsdd", address)
        self.assertEqual("Erdpy#123", password)





