from typing import Any

from erdpy.testnet.config import TestnetConfiguration


def patch(data: Any, testnet_config: TestnetConfiguration):
    data['DbLookupExtensions']['Enabled'] = True
    data['GeneralSettings']['SCDeployEnableEpoch'] = 0
    data['GeneralSettings']['BuiltInFunctionsEnableEpoch'] = 0
    data['GeneralSettings']['RelayedTransactionsEnableEpoch'] = 0
    data['GeneralSettings']['PenalizedTooMuchGasEnableEpoch'] = 0
    data['GeneralSettings']['SwitchJailWaitingEnableEpoch'] = 0
    data['GeneralSettings']['BelowSignedThresholdEnableEpoch'] = 0
    data['GeneralSettings']['SwitchHysteresisForMinNodesEnableEpoch'] = 1
    data['GeneralSettings']['TransactionSignedWithTxHashEnableEpoch'] = 0
    data['GeneralSettings']['MetaProtectionEnableEpoch'] = 0
    data['GeneralSettings']['AheadOfTimeGasUsageEnableEpoch'] = 0
    data['GeneralSettings']['GasPriceModifierEnableEpoch'] = 0

    # Make epochs shorter
    data['EpochStartConfig']['RoundsPerEpoch'] = 100


def patch_api(data: Any, testnet_config: TestnetConfiguration):
    routes = data['APIPackages']['transaction']['Routes']
    for route in routes:
        route["Open"] = True


def patch_system_smart_contracts(data: Any, testnet_config: TestnetConfiguration):
    data['StakingSystemSCConfig']['StakeEnableEpoch'] = 0
    data['StakingSystemSCConfig']['StakingV2Epoch'] = 1
    data['StakingSystemSCConfig']['DoubleKeyProtectionEnableEpoch'] = 0
    data['StakingSystemSCConfig']['ActivateBLSPubKeyMessageVerification'] = True
    data['ESDTSystemSCConfig']['EnabledEpoch'] = 0
    data['GovernanceSystemSCConfig']['EnabledEpoch'] = 0
    data['DelegationManagerSystemSCConfig']['EnabledEpoch'] = 1
    data['DelegationSystemSCConfig']['EnabledEpoch'] = 1
