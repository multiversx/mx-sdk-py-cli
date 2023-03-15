from typing import Any, Dict


class General:
    def __init__(self,
                 log_level: str,
                 genesis_delay: int):
        self.log_level: str = log_level
        self.genesis_delay: int = genesis_delay

    def override(self, other: Dict[str, Any]):
        self.log_level = other.get("log_level", self.log_level)
        self.genesis_delay = other.get("genesis_delay", self.genesis_delay)
