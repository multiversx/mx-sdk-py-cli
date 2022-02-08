from typing import Dict, Any

import erdpy.config

from erdpy.testnet.config import TestnetConfiguration
from erdpy.testnet.nodes_setup_json import CHAIN_ID

ConfigDict = Dict[str, Any]


def patch_config(data: ConfigDict, testnet_config: TestnetConfiguration):
    data['DbLookupExtensions']['Enabled'] = True

    general_settings: ConfigDict = dict()
    general_settings['ChainID'] = CHAIN_ID
    general_settings['MinTransactionVersion'] = 1
    general_settings['StartInEpochEnabled'] = True

    data['GeneralSettings'].update(general_settings)

    # Make epochs shorter - never below 100 rounds
    epoch_start_config: ConfigDict = dict()
    epoch_start_config['RoundsPerEpoch'] = 100
    epoch_start_config['MinRoundsBetweenEpochs'] = 20
    epoch_start_config['MinShuffledOutRestartThreshold'] = 0.1
    epoch_start_config['MaxShuffledOutRestartThreshold'] = 0.5

    data['EpochStartConfig'].update(epoch_start_config)

    # Always use the latest VM
    virtual_machine: Dict[str, Any] = dict()
    virtual_machine['Execution'] = dict()
    virtual_machine['Execution']['ArwenVersions'] = [{'StartEpoch': 0, 'Version': '*'}]
    virtual_machine['Querying'] = dict()
    virtual_machine['Querying']['NumConcurrentVMs'] = 1
    virtual_machine['Querying']['ArwenVersions'] = [{'StartEpoch': 0, 'Version': '*'}]

    data['VirtualMachine'].update(virtual_machine)


def patch_api(data: ConfigDict, testnet_config: TestnetConfiguration):
    routes = data['APIPackages']['transaction']['Routes']
    for route in routes:
        route['Open'] = True


def patch_enable_epochs(data: ConfigDict, testnet_config: TestnetConfiguration):
    enable_epochs: ConfigDict = dict()
    enable_epochs['SCDeployEnableEpoch'] = 0
    enable_epochs['BuiltInFunctionsEnableEpoch'] = 0
    enable_epochs['RelayedTransactionsEnableEpoch'] = 0
    enable_epochs['PenalizedTooMuchGasEnableEpoch'] = 0
    enable_epochs['SwitchJailWaitingEnableEpoch'] = 0
    enable_epochs['BelowSignedThresholdEnableEpoch'] = 0
    enable_epochs['SwitchHysteresisForMinNodesEnableEpoch'] = 1
    enable_epochs['TransactionSignedWithTxHashEnableEpoch'] = 1
    enable_epochs['MetaProtectionEnableEpoch'] = 1
    enable_epochs['AheadOfTimeGasUsageEnableEpoch'] = 0
    enable_epochs['GasPriceModifierEnableEpoch'] = 0
    enable_epochs['RepairCallbackEnableEpoch'] = 0
    enable_epochs['BlockGasAndFeesReCheckEnableEpoch'] = 0
    enable_epochs['ReturnDataToLastTransferEnableEpoch'] = 0
    enable_epochs['SenderInOutTransferEnableEpoch'] = 0
    enable_epochs['BalanceWaitingListsEnableEpoch'] = 0
    enable_epochs['SaveJailedAlwaysEnableEpoch'] = 0
    enable_epochs['StakeEnableEpoch'] = 0
    enable_epochs['StakingV2EnableEpoch'] = 1
    enable_epochs['DoubleKeyProtectionEnableEpoch'] = 0
    enable_epochs['ESDTEnableEpoch'] = 0
    enable_epochs['GovernanceEnableEpoch'] = 1
    enable_epochs['DelegationManagerEnableEpoch'] = 1
    enable_epochs['DelegationSmartContractEnableEpoch'] = 1
    enable_epochs['CorrectLastUnjailedEnableEpoch'] = 1
    enable_epochs['RelayedTransactionsV2EnableEpoch'] = 2
    enable_epochs['UnbondTokensV2EnableEpoch'] = 1
    enable_epochs['SaveJailedAlwaysEnableEpoch'] = 1
    enable_epochs['ReDelegateBelowMinCheckEnableEpoch'] = 1
    enable_epochs['ValidatorToDelegationEnableEpoch'] = 1
    enable_epochs['WaitingListFixEnableEpoch'] = 1000000
    enable_epochs['IncrementSCRNonceInMultiTransferEnableEpoch'] = 0
    enable_epochs['ESDTMultiTransferEnableEpoch'] = 0
    enable_epochs['GlobalMintBurnDisableEpoch'] = 0
    enable_epochs['ESDTTransferRoleEnableEpoch'] = 0
    enable_epochs['BuiltInFunctionOnMetaEnableEpoch'] = 0
    enable_epochs['ComputeRewardCheckpointEnableEpoch'] = 5
    enable_epochs['BackwardCompSaveKeyValueEnableEpoch'] = 5
    enable_epochs['SCRSizeInvariantCheckEnableEpoch'] = 5

    enable_epochs['MultiESDTTransferFixOnCallBackOnEnableEpoch'] = 0
    enable_epochs['ESDTNFTCreateOnMultiShard'] = 0
    enable_epochs['RemoveNonUpdatedStorageEnableEpoch'] = 0
    enable_epochs['FixOOGReturnCodeEnableEpoch'] = 0
    enable_epochs['AddTokensToDelegationEnableEpoch'] = 0
    enable_epochs['CorrectFirstQueuedEpoch'] = 0
    enable_epochs['MetaESDTSetEnableEpoch'] = 0
    enable_epochs['OptimizeGasUsedInCrossMiniBlocksEnableEpoch'] = 0
    enable_epochs['DeleteDelegatorAfterClaimRewardsEnableEpoch'] = 0

    enable_epochs['MaxNodesChangeEnableEpoch'] = [
        {'EpochEnable': 0, 'MaxNumNodes': 36, 'NodesToShufflePerShard': 4},
        {'EpochEnable': 1, 'MaxNumNodes': 56, 'NodesToShufflePerShard': 2}
    ]

    validate = erdpy.config.get_value('testnet.validate_expected_keys') == 'true'

    if validate:
        validate_expected_keys(data['EnableEpochs'], enable_epochs)
    data['EnableEpochs'].update(enable_epochs)

    gas_schedule = dict()
    gas_schedule['GasScheduleByEpochs'] = [
        {'StartEpoch': 0, 'FileName': 'gasScheduleV5.toml'}
    ]

    if validate:
        validate_expected_keys(data['GasSchedule'], gas_schedule)
    data['GasSchedule'].update(gas_schedule)


def patch_system_smart_contracts(data: ConfigDict, testnet_config: TestnetConfiguration):
    data['StakingSystemSCConfig']['ActivateBLSPubKeyMessageVerification'] = True
    data['ESDTSystemSCConfig']['EnabledEpoch'] = 0
    data['GovernanceSystemSCConfig']['EnabledEpoch'] = 0
    data['DelegationManagerSystemSCConfig']['EnabledEpoch'] = 1
    data['DelegationSystemSCConfig']['EnabledEpoch'] = 1


def validate_expected_keys(actual: ConfigDict, expected: ConfigDict):
    actual_keys = set(actual.keys())
    expected_keys = set(expected.keys())

    unrecognized_keys = actual_keys - expected_keys
    if len(unrecognized_keys) > 0:
        raise ValueError(f'unrecognized configuration keys {unrecognized_keys}')

    missing_keys = expected_keys - actual_keys
    if len(missing_keys) > 0:
        raise ValueError(f'missing configuration keys {missing_keys}')
