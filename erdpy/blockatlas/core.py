import logging

from erdpy.blockatlas.http_facade import do_get

logger = logging.getLogger("block-atlas")


class BlockAtlas:
    def __init__(self, url, coin):
        self.url = url
        self.coin = coin

    def get_current_block_number(self):
        pass

    def get_block_by_number(self, num: int):
        pass

    def get_txs_by_address(self, address: str):
        url = f"{self.url}/v2/{self.coin}/transactions/{address}"
        response = do_get(url)
        return response
