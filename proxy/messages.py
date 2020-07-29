from typing import Any, Dict


class NetworkConfig:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.num_shards = data.get("erd_num_shards_without_meta", 0)
        self.min_gas_price = data.get("erd_min_gas_price", 0)
        self.chain_id = data.get("erd_chain_id", 0)
        self.min_tx_version = data.get("erd_min_transaction_version", 0)
