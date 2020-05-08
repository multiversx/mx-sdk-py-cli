import logging

from erdpy.proxy.http_facade import do_get, do_post

METACHAIN_ID = 4294967295
ANY_SHARD_ID = 0

logger = logging.getLogger("proxy")


class ElrondProxy:
    def __init__(self, url):
        self.url = url

    def get_account_nonce(self, address):
        url = f"{self.url}/address/{address.bech32()}"
        response = do_get(url)
        nonce = response["account"]["nonce"]
        return nonce

    def get_account_balance(self, address):
        url = f"{self.url}/address/{address.bech32()}/balance"
        response = do_get(url)
        balance = response["balance"]
        return balance

    def get_account(self, address):
        url = f"{self.url}/address/{address.bech32()}"
        response = do_get(url)
        return response

    def get_account_transactions(self, address):
        url = f"{self.url}/address/{address.bech32()}/transactions"
        response = do_get(url)
        return response

    def get_num_shards(self):
        metrics = self._get_status_metrics(METACHAIN_ID)
        metric = metrics["erd_metric_cross_check_block_height"]
        # + 1 for metachain
        num_shards = metric.count(":") + 1
        return num_shards

    def get_last_block_nonce(self, shard_id):
        if shard_id == "metachain":
            metrics = self._get_status_metrics(METACHAIN_ID)
        else:
            metrics = self._get_status_metrics(shard_id)

        nonce = metrics["erd_probable_highest_nonce"]
        return nonce

    def get_gas_price(self):
        metrics = self._get_status_metrics(ANY_SHARD_ID)
        price = metrics["erd_min_gas_price"]
        return price

    def get_chain_id(self):
        metrics = self._get_status_metrics(ANY_SHARD_ID)
        chain_id = metrics["erd_chain_id"]
        return chain_id

    def _get_status_metrics(self, shard_id):
        url = f"{self.url}/node/status/{shard_id}"
        response = do_get(url)
        details = response["message"]["details"]
        return details

    def send_transaction(self, payload):
        url = f"{self.url}/transaction/send"
        response = do_post(url, payload)
        tx_hash = response["txHash"]
        return tx_hash

    def send_transactions(self, payload):
        url = f"{self.url}/transaction/send-multiple"
        response = do_post(url, payload)
        num_sent = response["numOfSentTxs"]
        return num_sent

    def query_contract(self, payload):
        url = f"{self.url}/vm-values/query"
        response = do_post(url, payload)
        return response
