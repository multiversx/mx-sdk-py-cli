import requests
import json
import logging

from http import HTTPStatus

METACHAIN_ID = 4294967295

logger = logging.getLogger("proxy")


class ProxyApiCaller:
    def __init__(self, url):
        self.url = url

    def get_account_nonce(self, address):
        req = f"{self.url}/address/{address}/nonce"
        try:
            response = requests.get(req)
            if response.status_code != HTTPStatus.OK:
                return "response status code " + str(response.status_code)

            parsed = json.loads(response.text)
            return print(parsed['nonce'])
        except:
            return print("cannot get nonce")

    def get_account_balance(self, address):
        req = f"{self.url}/address/{address}/balance"
        try:
            response = requests.get(req)
            if response.status_code != HTTPStatus.OK:
                return "response status code " + str(response.status_code)

            parsed = json.loads(response.text)
            return print(parsed['balance'])
        except:
            return print("cannot get balance")

    def get_account(self, address):
        req = f"{self.url}/address/{address}"
        try:
            response = requests.get(req)
            if response.status_code != HTTPStatus.OK:
                return "response status code " + str(response.status_code)
            parsed = json.loads(response.text)
            return print(parsed)
        except:
            return print("cannot get account")

    def get_num_shards(self):
        req = f"{self.url}/node/status/{METACHAIN_ID}"
        try:
            response = requests.get(req)
            if response.status_code != HTTPStatus.OK:
                return "response status code " + str(response.status_code)
            parsed = json.loads(response.content)
            metric = parsed['message']['erd_metric_cross_check_block_height']
            # number of shard will be equals with how many shard have notarized metachain + 1 (metachain shard)
            return print(metric.count(':') + 1)
        except:
            return print("cannot get number of shards")

    def get_last_block_nonce(self, shard_id):
        if shard_id == "metachain":
            req = f"{self.url}/node/status/{METACHAIN_ID}"
        else:
            req = f"{self.url}/node/status/{shard_id}"

        try:
            response = requests.get(req)
            if response.status_code != HTTPStatus.OK:
                return "response status code " + str(response.status_code)
            parsed = json.loads(response.content)
            metric = parsed['message']['erd_probable_highest_nonce']
            return print(metric)
        except:
            return print("cannot get last block nonce")
