from typing import Any, Dict

from multiversx_sdk_cli.testnet.config import TestnetConfiguration
from multiversx_sdk_cli.testnet.nodes_setup_json import CHAIN_ID

ConfigDict = Dict[str, Any]


def patch_config(data: ConfigDict, config: TestnetConfiguration):
    data['DbLookupExtensions']['Enabled'] = True

    general_settings: ConfigDict = dict()
    general_settings['ChainID'] = CHAIN_ID
    general_settings['StartInEpochEnabled'] = False
    general_settings['SetGuardianEpochsDelay'] = 1

    data['GeneralSettings'].update(general_settings)

    # Make epochs shorter
    epoch_start_config: ConfigDict = dict()
    epoch_start_config['RoundsPerEpoch'] = 100
    epoch_start_config['MinRoundsBetweenEpochs'] = 20

    data['EpochStartConfig'].update(epoch_start_config)

    # Always use the latest VM
    virtual_machine: Dict[str, Any] = dict()
    virtual_machine['Execution'] = dict()
    virtual_machine['Execution']['WasmVMVersions'] = [{'StartEpoch': 0, 'Version': '*'}]
    virtual_machine['Querying'] = dict()
    virtual_machine['Querying']['NumConcurrentVMs'] = 1
    virtual_machine['Querying']['WasmVMVersions'] = [{'StartEpoch': 0, 'Version': '*'}]

    data['VirtualMachine'].update(virtual_machine)


def patch_api(data: ConfigDict, config: TestnetConfiguration):
    routes = data['APIPackages']['transaction']['Routes']
    for route in routes:
        route['Open'] = True


def patch_enable_epochs(data: ConfigDict, config: TestnetConfiguration):
    pass
    # enable_epochs: ConfigDict = dict()
    # enable_epochs['SCDeployEnableEpoch'] = 0
    # enable_epochs['BuiltInFunctionsEnableEpoch'] = 0
    # enable_epochs['RelayedTransactionsEnableEpoch'] = 0
    # enable_epochs['PenalizedTooMuchGasEnableEpoch'] = 0
    # enable_epochs['SwitchJailWaitingEnableEpoch'] = 0
    # enable_epochs['BelowSignedThresholdEnableEpoch'] = 0
    # enable_epochs['AheadOfTimeGasUsageEnableEpoch'] = 0
    # enable_epochs['GasPriceModifierEnableEpoch'] = 0
    # enable_epochs['RepairCallbackEnableEpoch'] = 0
    # enable_epochs['BlockGasAndFeesReCheckEnableEpoch'] = 0
    # enable_epochs['ReturnDataToLastTransferEnableEpoch'] = 0
    # enable_epochs['SenderInOutTransferEnableEpoch'] = 0
    # enable_epochs['ESDTEnableEpoch'] = 0
    # enable_epochs['IncrementSCRNonceInMultiTransferEnableEpoch'] = 0
    # enable_epochs['ESDTMultiTransferEnableEpoch'] = 0
    # enable_epochs['GlobalMintBurnDisableEpoch'] = 0
    # enable_epochs['ESDTTransferRoleEnableEpoch'] = 0
    # enable_epochs['BuiltInFunctionOnMetaEnableEpoch'] = 0
    # enable_epochs['MultiESDTTransferFixOnCallBackOnEnableEpoch'] = 0
    # enable_epochs['ESDTNFTCreateOnMultiShard'] = 0
    # enable_epochs['RemoveNonUpdatedStorageEnableEpoch'] = 0
    # enable_epochs['FixOOGReturnCodeEnableEpoch'] = 0
    # enable_epochs['CorrectFirstQueuedEpoch'] = 0
    # enable_epochs['MetaESDTSetEnableEpoch'] = 0

    # data['EnableEpochs'].update(enable_epochs)
