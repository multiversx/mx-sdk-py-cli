from typing import Any, Dict, List

from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.localnet import wallets
from multiversx_sdk_cli.localnet.config_root import ConfigRoot
from multiversx_sdk_cli.localnet.genesis import (get_delegation_address,
                                                 is_foundational_node)

CHAIN_ID = "localnet"


def build(config: ConfigRoot) -> Any:
    num_validators = config.num_all_validators()
    initial_nodes: List[Dict[str, str]] = []

    for nickname, [pubkey, account] in wallets.get_validators(num_validators).items():
        entry = _build_initial_nodes_entry(nickname, pubkey, account)
        initial_nodes.append(entry)

    # Then, patch the list of initial nodes, so that higher indexes will become metachain nodes.
    num_metachain_nodes = config.metashard.num_validators
    num_nodes = len(initial_nodes)
    initial_nodes = initial_nodes[num_nodes - num_metachain_nodes:] + initial_nodes[:num_nodes - num_metachain_nodes]

    return {
        "startTime": config.genesis_time(),
        "roundDuration": config.general.round_duration_milliseconds,
        "consensusGroupSize": config.shards.consensus_size,
        "minNodesPerShard": config.shards.consensus_size,
        "metaChainConsensusGroupSize": config.metashard.consensus_size,
        "metaChainMinNodes": config.metashard.num_validators,
        "hysteresis": 0,
        "adaptivity": False,
        "chainID": CHAIN_ID,
        "minTransactionVersion": 1,
        "initialNodes": initial_nodes
    }


def _build_initial_nodes_entry(nickname: str, pubkey: str, account: Account) -> Dict[str, str]:
    address = get_delegation_address().bech32() if is_foundational_node(nickname) else account.address.bech32()

    return {
        "nickname": nickname,
        "address": address,
        "pubkey": pubkey,
    }
