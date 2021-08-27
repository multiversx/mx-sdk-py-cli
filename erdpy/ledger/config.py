class ElrondLedgerAppConfiguration:
    data_activated: bool
    account_index: int
    address_index: int
    version: str


def load_ledger_config_from_response(response: bytes) -> ElrondLedgerAppConfiguration:
    config = ElrondLedgerAppConfiguration()

    config.data_activated = False
    if response[0] == 0x01:
        config.data_activated = True

    config.account_index = response[1]
    config.address_index = response[2]

    version = str(response[3]) + "." + str(response[4]) + "." + str(response[5])
    config.version = version

    return config


def compare_versions(version1: str, version2: str) -> int:
    version1_tuple = version_tuple(version1)
    version2_tuple = version_tuple(version2)
    if version1_tuple == version2_tuple:
        return 0
    if version1_tuple < version2_tuple:
        return -1
    return 1


def version_tuple(v):
    filled = []
    for point in v.split("."):
        filled.append(point.zfill(8))
    return tuple(filled)
