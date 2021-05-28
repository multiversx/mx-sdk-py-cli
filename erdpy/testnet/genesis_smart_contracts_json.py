from typing import Any

from erdpy.testnet import genesis
from erdpy.testnet.config import TestnetConfiguration


def patch(data: Any, testnet_config: TestnetConfiguration):
    owner = genesis.get_owner_of_genesis_contracts()

    delegation_config = data[0]
    dns_config = data[1]

    delegation_config["owner"] = owner.address.bech32()
    dns_config["owner"] = owner.address.bech32()
    # registration price = 100 atoms of eGLD
    dns_config["init-parameters"] = "0064"
