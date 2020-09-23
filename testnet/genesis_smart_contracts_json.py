from typing import Any

from erdpy.testnet import wallets
from erdpy.testnet.config import TestnetConfiguration


def patch(data: Any, testnet_config: TestnetConfiguration):
    users = wallets.get_users()
    alice = users["alice"]

    # Set Alice as the owner of: delegation contract, dns contract
    data[0]["owner"] = alice.address.bech32()
    data[1]["owner"] = alice.address.bech32()
