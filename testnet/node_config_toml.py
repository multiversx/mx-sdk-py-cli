from typing import Any

from erdpy.testnet.config import TestnetConfiguration


def patch(data: Any, testnet_config: TestnetConfiguration):
    data['DbLookupExtensions']['Enabled'] = True
