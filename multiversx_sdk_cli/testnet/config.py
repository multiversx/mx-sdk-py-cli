import logging
import time
from pathlib import Path
from typing import Any, Dict, List

import multiversx_sdk_cli.utils as utils
from multiversx_sdk_cli.testnet import config_default

logger = logging.getLogger("localnet")


class Node:
    def __init__(self, index: int, folder: Path, shard: str, api_port: int) -> None:
        self.index = index
        self.folder = folder
        self.shard = shard
        self.api_port = api_port

    def key_file_path(self):
        return self.folder / "config" / "validatorKey.pem"

    def api_address(self):
        return f"http://localhost:{self.api_port}"

    def __repr__(self) -> str:
        return f"Node {self.index}, shard={self.shard}, port={self.api_port}, folder={self.folder}"


class TestnetConfiguration:
    def __init__(self):
        self.general = config_default.general
        self.software = config_default.software
        self.metashard = config_default.metashard
        self.shards = config_default.shards
        self.networking = config_default.networking

    def override(self, other: Dict[str, Any]):
        self.general.override(other.get("general", dict()))
        self.software.override(other.get("software", dict()))
        self.metashard.override(other.get("metashard", dict()))
        self.shards.override(other.get("shards", dict()))
        self.networking.override(other.get("networking", dict()))

    @classmethod
    def from_file(cls, path: Path):
        path = path.expanduser().resolve()
        instance = cls()
        local_config_dict = utils.read_toml_file(path)
        instance.override(local_config_dict)

        return instance

    def root(self) -> Path:
        return Path("localnet").resolve()

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

    def num_all_nodes(self) -> int:
        return self.num_all_validators() + self.num_all_observers()

    def num_all_validators(self) -> int:
        return self.shards.num_shards * self.shards.num_validators_per_shard + self.metashard.num_validators

    def num_all_observers(self) -> int:
        return self.shards.num_shards * self.shards.num_observers_per_shard + self.metashard.num_observers

    def validators(self) -> List[Node]:
        first_port = self.networking.port_first_validator_rest_api
        nodes: List[Node] = []

        for i, folder in enumerate(self.validator_folders()):
            shard = self._get_shard_of_validator(i)
            port = first_port + i
            nodes.append(Node(index=i, folder=folder, shard=str(shard), api_port=port))

        return nodes

    def _get_shard_of_validator(self, observer_index: int) -> int:
        shard = int(observer_index // self.shards.num_validators_per_shard)
        return shard if shard < self.shards.num_shards else 4294967295

    def validator_folders(self):
        return [self.root() / "validator{:02}".format(i) for i in range(self.num_all_validators())]

    def validator_config_folders(self) -> List[Path]:
        return [folder / "config" for folder in self.validator_folders()]

    def observers(self) -> List[Node]:
        first_port = self.networking.port_first_observer_rest_api
        nodes: List[Node] = []

        for i, folder in enumerate(self.observer_folders()):
            shard = self._get_shard_of_observer(i)
            port = first_port + i
            nodes.append(Node(index=i, folder=folder, shard=str(shard), api_port=port))

        return nodes

    def _get_shard_of_observer(self, observer_index: int):
        shard = int(observer_index // self.shards.num_observers_per_shard)
        return shard if shard < self.shards.num_shards else 4294967295

    def observer_config_folders(self) -> List[Path]:
        return [folder / "config" for folder in self.observer_folders()]

    def observer_folders(self) -> List[Path]:
        return [self.root() / "observer{:02}".format(i) for i in range(self.num_all_observers())]

    # TODO PRINT
    # def observer_addresses(self):
    #     host = self.networking["host"]
    #     first_port = self.networking["port_first_observer_rest_api"]
    #     for port in range(self.num_all_observers()):
    #         port = first_port + port
    #         yield f"http://{host}:{port}"

    # TODO PRINT
    # def validator_addresses(self):
    #     host = self.networking["host"]
    #     first_port = self.networking["port_first_observer_rest_api"]
    #     for port in range(self.num_all_observers()):
    #         port = first_port + port
    #         yield f"http://{host}:{port}"

    def api_addresses_sharded_for_proxy_config(self) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []

        for node in self.observers():
            nodes.append({
                "ShardId": int(node.shard),
                "Address": node.api_address(),
                "Type": "Observer"
            })

        for node in self.validators():
            nodes.append({
                "ShardId": int(node.shard),
                "Address": node.api_address(),
                "Type": "Validator"
            })

        return nodes
