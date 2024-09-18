from typing import Any, Dict

from multiversx_sdk_cli.localnet.config_root import ConfigRoot
from multiversx_sdk_cli.localnet.nodes_setup_json import CHAIN_ID

ConfigDict = Dict[str, Any]


def patch_config(data: ConfigDict, config: ConfigRoot):
    data['GeneralSettings']['ChainID'] = CHAIN_ID

    # "--operation-mode=historical-balances" is not available for nodes,
    # since << validator cannot be a full archive node >>,
    # but we attempt to set the "deep-history" mode as follows:
    data['DbLookupExtensions']['Enabled'] = True
    data['GeneralSettings']['StartInEpochEnabled'] = False
    data['StateTriesConfig']['AccountsStatePruningEnabled'] = False
    data['StoragePruning']['ObserverCleanOldEpochsData'] = False
    data['StoragePruning']['AccountsTrieCleanOldEpochsData'] = False

    # Make epochs shorter
    epoch_start_config: ConfigDict = dict()
    epoch_start_config['RoundsPerEpoch'] = config.general.rounds_per_epoch
    epoch_start_config['MinRoundsBetweenEpochs'] = int(config.general.rounds_per_epoch / 4)

    data['EpochStartConfig'].update(epoch_start_config)

    # Always use the latest VM
    data['VirtualMachine']['Execution']['WasmVMVersions'] = [{'StartEpoch': 0, 'Version': '*'}]
    data['VirtualMachine']['Querying']['WasmVMVersions'] = [{'StartEpoch': 0, 'Version': '*'}]


def patch_api(data: ConfigDict, config: ConfigRoot):
    routes = data['APIPackages']['transaction']['Routes']
    for route in routes:
        route['Open'] = True


def patch_enable_epochs(data: ConfigDict, config: ConfigRoot):
    enable_epochs = data["EnableEpochs"]
    enable_epochs['SCDeployEnableEpoch'] = 0
    enable_epochs['BuiltInFunctionsEnableEpoch'] = 0
    enable_epochs['RelayedTransactionsEnableEpoch'] = 0
    enable_epochs['PenalizedTooMuchGasEnableEpoch'] = 0
    enable_epochs['AheadOfTimeGasUsageEnableEpoch'] = 0
    enable_epochs['GasPriceModifierEnableEpoch'] = 0
    enable_epochs['RepairCallbackEnableEpoch'] = 0
    enable_epochs['ReturnDataToLastTransferEnableEpoch'] = 0
    enable_epochs['SenderInOutTransferEnableEpoch'] = 0
    enable_epochs['ESDTEnableEpoch'] = 0
    enable_epochs['IncrementSCRNonceInMultiTransferEnableEpoch'] = 0
    enable_epochs['ESDTMultiTransferEnableEpoch'] = 0
    enable_epochs['GlobalMintBurnDisableEpoch'] = 0
    enable_epochs['ESDTTransferRoleEnableEpoch'] = 0
    enable_epochs['BuiltInFunctionOnMetaEnableEpoch'] = 0
    enable_epochs['MultiESDTTransferFixOnCallBackOnEnableEpoch'] = 0
    enable_epochs['ESDTNFTCreateOnMultiShard'] = 0
    enable_epochs['MetaESDTSetEnableEpoch'] = 0
    enable_epochs['DelegationManagerEnableEpoch'] = 0

    max_nodes_change_enable_epoch = enable_epochs['MaxNodesChangeEnableEpoch']
    last_entry = max_nodes_change_enable_epoch[-1]
    penultimate_entry = max_nodes_change_enable_epoch[-2]
    last_entry['MaxNumNodes'] = penultimate_entry['MaxNumNodes'] - (config.shards.num_shards + 1) * penultimate_entry['NodesToShufflePerShard']
