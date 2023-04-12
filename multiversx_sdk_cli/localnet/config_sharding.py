from typing import Any, Dict

from multiversx_sdk_cli.localnet.config_part import ConfigPart


class Metashard(ConfigPart):
    def __init__(self,
                 consensus_size: int,
                 num_observers: int,
                 num_validators: int):
        self.consensus_size: int = consensus_size
        self.num_observers: int = num_observers
        self.num_validators: int = num_validators

    def get_name(self) -> str:
        return "metashard"

    def _do_override(self, other: Dict[str, Any]):
        self.consensus_size = other.get("consensus_size", self.consensus_size)
        self.num_observers = other.get("num_observers", self.num_observers)
        self.num_validators = other.get("num_validators", self.num_validators)


class RegularShards(ConfigPart):
    def __init__(self,
                 num_shards: int,
                 consensus_size: int,
                 num_observers_per_shard: int,
                 num_validators_per_shard: int):
        self.num_shards: int = num_shards
        self.consensus_size: int = consensus_size
        self.num_observers_per_shard: int = num_observers_per_shard
        self.num_validators_per_shard: int = num_validators_per_shard

    def get_name(self) -> str:
        return "sharding"

    def _do_override(self, other: Dict[str, Any]):
        self.num_shards = other.get("num_shards", self.num_shards)
        self.consensus_size = other.get("consensus_size", self.consensus_size)
        self.num_observers_per_shard = other.get("num_observers_per_shard", self.num_observers_per_shard)
        self.num_validators_per_shard = other.get("num_validators_per_shard", self.num_validators_per_shard)
