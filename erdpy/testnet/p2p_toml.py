from typing import Any

from erdpy.testnet.config import TestnetConfiguration

PROTOCOL_ID = '/erd/kad/sandbox'


def patch(data: Any, testnet_config: TestnetConfiguration, node_index: int, port_first: int) -> Any:
    data['Node']['Port'] = str(port_first + node_index)
    data['Node']['ThresholdMinConnectedPeers'] = 1
    data['KadDhtPeerDiscovery']['InitialPeerList'] = [
        testnet_config.seednode_address()
    ]
    data['KadDhtPeerDiscovery']['ProtocolID'] = PROTOCOL_ID
    data['Sharding']['Type'] = "NilListSharder"


def patch_for_seednode(data: Any, testnet_config: TestnetConfiguration):
    port_seednode = testnet_config.networking['port_seednode']

    data['Node']['Port'] = str(port_seednode)
    data['Node']['MaximumExpectedPeerCount'] = 16
    data['KadDhtPeerDiscovery']['ProtocolID'] = PROTOCOL_ID
    data['Sharding']['Type'] = "NilListSharder"
