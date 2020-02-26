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
        metrics, ok = self.__get_status_metrics(METACHAIN_ID)
        if not ok:
            return print("cannot get number of shards")

        metric = metrics['erd_metric_cross_check_block_height']
        # number of shard will be equals with how many shard have notarized metachain + 1 (metachain shard)
        return print(metric.count(':') + 1)

    def get_last_block_nonce(self, shard_id):
        if shard_id == "metachain":
            metrics, ok = self.__get_status_metrics(METACHAIN_ID)
        else:
            metrics, ok = self.__get_status_metrics(shard_id)

        if not ok:
            return print("cannot get last block nonce")
        return print(metrics['erd_probable_highest_nonce'])

    def get_gas_price(self):
        metrics, ok = self.__get_status_metrics(0)
        if not ok:
            return print("cannot get gas price")

        return print(metrics['erd_min_gas_price'])

    def get_chain_id(self):
        metrics, ok = self.__get_status_metrics(0)
        if not ok:
            return print("cannot get chain id")

        return print(metrics['erd_chain_id'])

    def __get_status_metrics(self, shard_id):
        req = f"{self.url}/node/status/{shard_id}"
        try:
            response = requests.get(req)
            if response.status_code != HTTPStatus.OK:
                return None, False
            parsed = json.loads(response.content)
            return parsed['message'], True
        except:
            return None, False
