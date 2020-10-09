from typing import Any

from erdpy.testnet.config import TestnetConfiguration


def patch(data: Any, testnet_config: TestnetConfiguration):
    data['DbLookupExtensions']['Enabled'] = True
    data['GeneralSettings']['SCDeployEnableEpoch'] = 0
    data['GeneralSettings']['BuiltInFunctionsEnableEpoch'] = 0
    data['GeneralSettings']['RelayedTransactionsEnableEpoch'] = 0
    data['GeneralSettings']['PenalizedTooMuchGasEnableEpoch'] = 0
    data['GeneralSettings']['SwitchJailWaitingEnableEpoch'] = 0


def patch_api(data: Any, testnet_config: TestnetConfiguration):
    routes = data['APIPackages']['transaction']['Routes']
    for route in routes:
        route["Open"] = True


def patch_system_smart_contracts(data: Any, testnet_config: TestnetConfiguration):
    data['StakingSystemSCConfig']['StakeEnableEpoch'] = 0
    data['StakingSystemSCConfig']['ActivateBLSPubKeyMessageVerification'] = True
    data['ESDTSystemSCConfig']['EnabledEpoch'] = 0

