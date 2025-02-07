import logging
import time
from pathlib import Path
from typing import Any, Dict, List

import toml

from multiversx_sdk_cli.localnet import config_default
from multiversx_sdk_cli.localnet.config_part import ConfigPart
from multiversx_sdk_cli.localnet.config_sharding import Metashard, RegularShards
from multiversx_sdk_cli.localnet.constants import METACHAIN_ID
from multiversx_sdk_cli.localnet.node import Node

logger = logging.getLogger("localnet")


class ConfigRoot(ConfigPart):
    shards: RegularShards
    metashard: Metashard

    def __init__(self):
        self.general = config_default.general
        self.software = config_default.software
        self.metashard = config_default.metashard
        self.shards = config_default.shards
        self.networking = config_default.networking

    def get_name(self) -> str:
        return "(configuration root)"

    def _do_override(self, other: Dict[str, Any]):
        self.general.override(other.get(self.general.get_name(), dict()))
        self.software.override(other.get(self.software.get_name(), dict()))
        self.metashard.override(other.get(self.metashard.get_name(), dict()))
        self.shards.override(other.get(self.shards.get_name(), dict()))
        self.networking.override(other.get(self.networking.get_name(), dict()))

    @classmethod
    def from_file(cls, path: Path):
        logger.info(f"Loading localnet configuration from: {path}")

        path = path.expanduser().resolve()
        instance = cls()
        local_config_dict = toml.load(str(path))
        instance.override(local_config_dict)

        return instance

    def save(self, path: Path):
        path = path.expanduser().resolve()
        with open(path, "w") as f:
            toml.dump(self.to_dictionary(), f)

        logger.info(f"Saved localnet configuration to: {path}")

    def root(self) -> Path:
        return Path("localnet").expanduser().resolve()

    def seednode_folder(self):
        return self.root() / "seednode"

    def seednode_config_folder(self):
        return self.seednode_folder() / "config"

    def proxy_folder(self):
        return self.root() / "proxy"

    def proxy_config_folder(self):
        return self.proxy_folder() / "config"

    def all_nodes_folders(self):
        return self.validator_folders() + self.observer_folders()

    def all_nodes_config_folders(self):
        return self.validator_config_folders() + self.observer_config_folders()

    def genesis_time(self):
        return int(time.time()) + int(self.general.genesis_delay_seconds)

    def seednode_address(self):
        host = self.networking.host
        port = self.networking.port_seednode
        identifier = self.networking.p2p_id_seednode
        return f"/ip4/{host}/tcp/{port}/p2p/{identifier}"

    def seednode_api_interface(self):
        port = self.networking.port_seednode_rest_api
        return f"{self.networking.host}:{port}"

    def seednode_api_address(self):
        return f"http://{self.seednode_api_interface()}"

    def num_all_nodes(self) -> int:
        return self.num_all_validators() + self.num_all_observers()

    def num_all_validators(self) -> int:
        return self.shards.num_shards * self.shards.num_validators_per_shard + self.metashard.num_validators

    def num_all_observers(self) -> int:
        return self.shards.num_shards * self.shards.num_observers_per_shard + self.metashard.num_observers

    def all_nodes(self) -> List[Node]:
        return self.validators() + self.observers()

    def validators(self) -> List[Node]:
        first_port = self.networking.port_first_validator_rest_api
        nodes: List[Node] = []

        for i, folder in enumerate(self.validator_folders()):
            shard = self._get_shard_of_validator(i)
            host = self.networking.host
            port = first_port + i
            nodes.append(Node(index=i, folder=folder, shard=str(shard), host=host, api_port=port))

        return nodes

    def _get_shard_of_validator(self, observer_index: int) -> int:
        shard = int(observer_index // self.shards.num_validators_per_shard)
        return shard if shard < self.shards.num_shards else METACHAIN_ID

    def validator_folders(self):
        return [self.root() / "validator{:02}".format(i) for i in range(self.num_all_validators())]

    def validator_config_folders(self) -> List[Path]:
        return [folder / "config" for folder in self.validator_folders()]

    def observers(self) -> List[Node]:
        first_port = self.networking.port_first_observer_rest_api
        nodes: List[Node] = []

        for i, folder in enumerate(self.observer_folders()):
            shard = self._get_shard_of_observer(i)
            host = self.networking.host
            port = first_port + i
            nodes.append(Node(index=i, folder=folder, shard=str(shard), host=host, api_port=port))

        return nodes

    def _get_shard_of_observer(self, observer_index: int):
        shard = int(observer_index // self.shards.num_observers_per_shard)
        return shard if shard < self.shards.num_shards else METACHAIN_ID

    def observer_config_folders(self) -> List[Path]:
        return [folder / "config" for folder in self.observer_folders()]

    def observer_folders(self) -> List[Path]:
        return [self.root() / "observer{:02}".format(i) for i in range(self.num_all_observers())]

    def api_addresses_sharded_for_proxy_config(self) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []

        for node in self.observers():
            nodes.append(
                {
                    "ShardId": int(node.shard),
                    "Address": node.api_address(),
                    "Type": "Observer",
                }
            )

        for node in self.validators():
            nodes.append(
                {
                    "ShardId": int(node.shard),
                    "Address": node.api_address(),
                    "Type": "Validator",
                }
            )

        return nodes

    def to_dictionary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()
        result[self.general.get_name()] = self.general.to_dictionary()
        result[self.software.get_name()] = self.software.to_dictionary()
        result[self.metashard.get_name()] = self.metashard.to_dictionary()
        result[self.shards.get_name()] = self.shards.to_dictionary()
        result[self.networking.get_name()] = self.networking.to_dictionary()

        return result
