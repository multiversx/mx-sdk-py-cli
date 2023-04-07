from pathlib import Path

from multiversx_sdk_cli.testnet.config_general import General
from multiversx_sdk_cli.testnet.config_networking import Networking
from multiversx_sdk_cli.testnet.config_sharding import Metashard, RegularShards
from multiversx_sdk_cli.testnet.config_software import (
    Software, SoftwareLocalPrebuiltCmdFolders, SoftwareLocalSourceFolders,
    SoftwareRemoteArchives, SoftwareResolution)

general = General(
    log_level="*:DEBUG",
    genesis_delay_seconds=10,
    rounds_per_epoch=100,
    round_duration_milliseconds=6000
)

software = Software(
    resolution=SoftwareResolution.RemoteArchives,
    remote_archives=SoftwareRemoteArchives(
        downloads_folder=Path("~/multiversx-sdk").expanduser().resolve() / "testnet_software_archives",
        mx_chain_go="https://github.com/multiversx/mx-chain-go/archive/refs/heads/master.zip",
        mx_chain_proxy_go="https://github.com/multiversx/mx-chain-proxy-go/archive/refs/heads/master.zip"
    ),
    local_source_folders=SoftwareLocalSourceFolders(),
    local_prebuilt_cmd_folders=SoftwareLocalPrebuiltCmdFolders()
)

metashard = Metashard(
    consensus_size=1,
    num_observers=0,
    num_validators=1,
)

shards = RegularShards(
    num_shards=1,
    consensus_size=1,
    num_observers_per_shard=0,
    num_validators_per_shard=1,
)

networking = Networking(
    host="127.0.0.1",
    port_seednode=9999,
    p2p_id_seednode="16Uiu2HAkx4QqgXXDdHdUWbLu5kxhd3Uo2hqB2FfCxmxH5Sd7bZFk",
    port_proxy=7950,
    port_first_observer=21100,
    port_first_observer_rest_api=10000,
    port_first_validator=21500,
    port_first_validator_rest_api=10100
)
