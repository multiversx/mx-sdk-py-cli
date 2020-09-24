from typing import Any

from erdpy.testnet import genesis
from erdpy.testnet.config import TestnetConfiguration


def patch(data: Any, testnet_config: TestnetConfiguration):
    owner = genesis.get_owner_of_genesis_contracts()

    data[0]["owner"] = owner.address.bech32()
    data[1]["owner"] = owner.address.bech32()
