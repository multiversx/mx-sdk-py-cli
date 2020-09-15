from typing import Any

from erdpy.accounts import Account
from erdpy.testnet import wallets
from erdpy.testnet.config import TestnetConfiguration


def build(testnet_config: TestnetConfiguration) -> Any:
    num_validators = testnet_config.num_all_validators()
    initial_nodes = []

    for nickname, validator in wallets.get_validators(num_validators).items():
        entry = _build_initial_nodes_entry(nickname, *validator)
        initial_nodes.append(entry)

    return {
        "startTime": testnet_config.genesis_time(),
        "roundDuration": 6000,
        "consensusGroupSize": testnet_config.shards["consensus_size"],
        "minNodesPerShard": testnet_config.shards["consensus_size"],
        "metaChainConsensusGroupSize": testnet_config.metashard["consensus_size"],
        "metaChainMinNodes": testnet_config.metashard["validators"],
        "hysteresis": 0,
        "adaptivity": False,
        "chainID": "local-testnet",
        "minTransactionVersion": 1,
        "initialNodes": initial_nodes
    }


def _build_initial_nodes_entry(nickname: str, pubkey: str, account: Account) -> Any:
    return {
        "nickname": nickname,
        "address": account.address.bech32(),
        "pubkey": pubkey,
    }
