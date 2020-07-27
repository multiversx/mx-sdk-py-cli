import logging

from typing import Any
from erdpy.accounts import Address


from erdpy.proxy.http_facade import do_get, do_post

METACHAIN_ID = 4294967295
ANY_SHARD_ID = 0

logger = logging.getLogger("proxy")


class ElrondProxy:
    def __init__(self, url: str):
        self.url = url

    def get_account_nonce(self, address: Address):
        url = f"{self.url}/address/{address.bech32()}"
        response = do_get(url)
        nonce = response["account"]["nonce"]
        return nonce

    def get_account_balance(self, address: Address):
        url = f"{self.url}/address/{address.bech32()}/balance"
        response = do_get(url)
        balance = response["balance"]
        return balance

    def get_account(self, address: Address):
        url = f"{self.url}/address/{address.bech32()}"
        response = do_get(url)
        return response

    def get_account_transactions(self, address: Address):
        TRUNCATE_DATA_THRESHOLD = 75

        url = f"{self.url}/address/{address.bech32()}/transactions"
        response = do_get(url)
        transactions = response.get("transactions", [])
        for transaction in transactions:
            data = transaction.get("data", "")
            data = (data[:TRUNCATE_DATA_THRESHOLD] + ' ... truncated ...') if len(data) > TRUNCATE_DATA_THRESHOLD else data
            transaction["data"] = data
        return transactions

    def get_num_shards(self):
        network_config = self._get_network_config()
        num_shards_without_meta = network_config.get("erd_num_shards_without_meta", 0)
        return num_shards_without_meta + 1

    def get_last_block_nonce(self, shard_id):
        if shard_id == "metachain":
            metrics = self._get_network_status(METACHAIN_ID)
        else:
            metrics = self._get_network_status(shard_id)

        nonce = metrics["erd_nonce"]
        return nonce

    def get_gas_price(self):
        network_config = self._get_network_config()
        price = network_config["erd_min_gas_price"]
        return price

    def get_chain_id(self):
        network_config = self._get_network_config()
        chain_id = network_config["erd_chain_id"]
        return chain_id

    def _get_network_status(self, shard_id):
        url = f"{self.url}/network/status/{shard_id}"
        response = do_get(url)
        payload = response.get("status", None)
        if not payload:
            payload = response.get("message", None)
            if payload:
                payload = payload.get("status", None)

        return payload

    def _get_network_config(self):
        url = f"{self.url}/network/config"
        response = do_get(url)
        payload = response.get("config", None)
        if not payload:
            payload = response.get("message", None)
            if payload:
                payload = payload.get("config", None)

        return payload

    def send_transaction(self, payload):
        url = f"{self.url}/transaction/send"
        response = do_post(url, payload)
        tx_hash = response["txHash"]
        return tx_hash

    def send_transactions(self, payload):
        url = f"{self.url}/transaction/send-multiple"
        response = do_post(url, payload)
        # Proxy and Observers have different response format:
        num_sent = response.get("numOfSentTxs", 0) or response.get("txsSent", 0)
        hashes = response.get("txsHashes", None)
        return num_sent, hashes

    def query_contract(self, payload):
        url = f"{self.url}/vm-values/query"
        response = do_post(url, payload)
        return response

    def get_block_by_nonce(self, nonce, with_txs=False):
        url = f"{self.url}/block/by-nonce/{nonce}?withTxs={with_txs}"
        response = do_get(url)
        return response

    def get_block_by_hash(self, block_hash, with_txs=False):
        url = f"{self.url}/block/by-hash/{block_hash}?withTxs={with_txs}"
        response = do_get(url)
        return response

    def get_transaction(self, tx_hash: str, sender_address: str) -> Any:
        url = f"{self.url}/transaction/{tx_hash}"
        if sender_address != "":
            url += f"?sender={sender_address}"

        response = do_get(url)
        return response
