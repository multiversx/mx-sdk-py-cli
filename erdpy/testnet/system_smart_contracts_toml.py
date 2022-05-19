from typing import Any

from erdpy.testnet.config import TestnetConfiguration


def patch(data: Any, testnet_config: TestnetConfiguration) -> Any:
    data['ESDTSystemSCConfig']['BaseIssuingCost'] = testnet_config.systemSmartContracts.get("ESDTBaseIssuingCost")
