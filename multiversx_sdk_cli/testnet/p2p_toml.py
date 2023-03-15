from typing import Any

from multiversx_sdk_cli.testnet.config import TestnetConfiguration

PROTOCOL_ID = '/erd/kad/sandbox'


def patch(data: Any, config: TestnetConfiguration, node_index: int, port_first: int) -> Any:
    data['Node']['Port'] = str(port_first + node_index)
    data['Node']['ThresholdMinConnectedPeers'] = 1
    data['KadDhtPeerDiscovery']['InitialPeerList'] = [
        config.seednode_address()
    ]
    data['KadDhtPeerDiscovery']['ProtocolID'] = PROTOCOL_ID
    data['Sharding']['Type'] = "NilListSharder"


def patch_for_seednode(data: Any, config: TestnetConfiguration):
    port_seednode = config.networking.port_seednode

    data['Node']['Port'] = str(port_seednode)
    data['Node']['MaximumExpectedPeerCount'] = 16
    data['KadDhtPeerDiscovery']['ProtocolID'] = PROTOCOL_ID
    data['Sharding']['Type'] = "NilListSharder"
