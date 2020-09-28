from typing import Any

from erdpy.testnet.config import TestnetConfiguration


def patch(data: Any, testnet_config: TestnetConfiguration):
    data['DbLookupExtensions']['Enabled'] = True


def patch_api(data: Any, testnet_config: TestnetConfiguration):
    routes = data['APIPackages']['transaction']['Routes']
    for route in routes:
        route["Open"] = True
