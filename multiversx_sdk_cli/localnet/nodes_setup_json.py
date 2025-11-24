from typing import Any, Dict, List

from multiversx_sdk_cli.localnet import wallets
from multiversx_sdk_cli.localnet.config_root import ConfigRoot

CHAIN_ID = "localnet"


def build(config: ConfigRoot) -> Any:
    num_validators = config.num_all_validators()
    initial_nodes: List[Dict[str, str]] = []

    for nickname, [pubkey, account] in wallets.get_validators(num_validators).items():
        entry = {
            "nickname": nickname,
            "address": account.address.to_bech32(),
            "pubkey": pubkey,
        }

        initial_nodes.append(entry)

    # Then, patch the list of initial nodes, so that higher indexes will become metachain nodes.
    num_metachain_nodes = config.metashard.num_validators
    num_nodes = len(initial_nodes)
    initial_nodes = initial_nodes[num_nodes - num_metachain_nodes :] + initial_nodes[: num_nodes - num_metachain_nodes]

    return {
        "startTime": config.genesis_time(),
        "initialNodes": initial_nodes,
    }
