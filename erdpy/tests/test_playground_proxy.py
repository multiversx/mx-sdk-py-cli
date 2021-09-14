import unittest

import requests


class TestPlaygroundElrondProxy(unittest.TestCase):
    @unittest.skip('manual run only')
    def test_do_request(self):
        # use a valid proxy address
        url = "http://localhost:8001"
        # use a valid account address
        address = "78570f77898db9f59b8377192f3e657eac484bb1b4ed245e594bbc67d894c5ad"
        response = requests.get(url + "/address/" + address + "/nonce")
        print("response status code " + str(response.status_code))
        print(response.json())
        self.assertTrue(self, response is not None)

    @unittest.skip('manual run only')
    def test_do_request_node_status(self):
        # use a valid proxy address
        url = "http://localhost:8001"
        # use a valid shard id
        shard_id = "0"

        response = requests.get(f"{url}/network/status/{shard_id}")
        print("response status code " + str(response.status_code))
        print(response.json())
        self.assertTrue(self, response is not None)
