from typing import Any, Dict

from multiversx_sdk_cli.localnet.config_part import ConfigPart


class General(ConfigPart):
    def __init__(
        self,
        log_level: str,
        genesis_delay_seconds: int,
        rounds_per_epoch: int,
        round_duration_milliseconds: int,
        rounds_per_epoch_in_supernova: int,
        round_duration_milliseconds_in_supernova: int
    ):
        self.log_level = log_level
        self.genesis_delay_seconds = genesis_delay_seconds
        self.rounds_per_epoch = rounds_per_epoch
        self.round_duration_milliseconds = round_duration_milliseconds
        self.rounds_per_epoch_in_supernova = rounds_per_epoch_in_supernova
        self.round_duration_milliseconds_in_supernova = round_duration_milliseconds_in_supernova

    def get_name(self) -> str:
        return "general"

    def _do_override(self, other: Dict[str, Any]):
        self.log_level = other.get("log_level", self.log_level)
        self.genesis_delay_seconds = other.get("genesis_delay_seconds", self.genesis_delay_seconds)
        self.rounds_per_epoch = other.get("rounds_per_epoch", self.rounds_per_epoch)
        self.round_duration_milliseconds = other.get("round_duration_milliseconds", self.round_duration_milliseconds)
        self.rounds_per_epoch_in_supernova = other.get("rounds_per_epoch_in_supernova", self.rounds_per_epoch_in_supernova)
        self.round_duration_milliseconds_in_supernova = other.get("round_duration_milliseconds_in_supernova", self.round_duration_milliseconds_in_supernova)
