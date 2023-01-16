
import logging
import sys

import requests
import toml
from multiversx_sdk_cli.diskcache import DiskCache
from multiversx_sdk_network_providers.proxy_network_provider import ProxyNetworkProvider

logger = logging.getLogger("eei")


class ActivationEpochsInfo(DiskCache):
    def __init__(self, network_name: str, proxy_url: str, enable_epochs_url: str) -> None:
        super().__init__(cache_name="projects.eei.ActivationEpochsInfo", max_age=60 * 30)
        self.network_name = network_name
        self.proxy_url = proxy_url
        self.enable_epochs_url = enable_epochs_url

    def is_flag_active(self, flag_name: str):
        current_epoch_key = f"epoch:{self.proxy_url}"
        enable_epochs_key = f"config:{self.enable_epochs_url}"

        current_epoch = self.get_and_cache_item(current_epoch_key, self._fetch_current_epoch)
        enable_epochs = self.get_and_cache_item(enable_epochs_key, self._fetch_enable_epochs)
        enable_epoch = enable_epochs.get(flag_name, sys.maxsize)
        return current_epoch >= enable_epoch

    def _fetch_current_epoch(self):
        logger.info(f"fetch_current_epoch: {self.proxy_url}")
        proxy = ProxyNetworkProvider(self.proxy_url)
        return proxy.get_network_status().epoch_number

    def _fetch_enable_epochs(self):
        logger.info(f"fetch_enable_epochs: {self.enable_epochs_url}")
        response = requests.get(self.enable_epochs_url)
        response.raise_for_status()
        enable_epochs = toml.loads(response.text).get("EnableEpochs", dict())
        return dict(enable_epochs)
