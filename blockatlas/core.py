import logging

from erdpy.blockatlas.http_facade import do_get, do_post

logger = logging.getLogger("block-atlas")


class BlockAtlas:
    def __init__(self, url):
        self.url = url

    def get_txs_by_address(self):
        pass

    def current_block_number(self):
        pass

    def get_block_by_number(self, num: int):
        pass