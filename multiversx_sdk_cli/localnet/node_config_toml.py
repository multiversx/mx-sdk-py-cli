from typing import Any, Dict, Optional

from multiversx_sdk_cli.localnet.config_root import ConfigRoot
from multiversx_sdk_cli.localnet.constants import ROUNDS_PER_EPOCH_TO_MIN_ROUNDS_BETWEEN_EPOCHS_RATIO
from multiversx_sdk_cli.localnet.nodes_setup_json import CHAIN_ID

ConfigDict = Dict[str, Any]


def patch_config(data: ConfigDict, config: ConfigRoot, supernova_activation_epoch: Optional[int] = None):
    data["GeneralSettings"]["ChainID"] = CHAIN_ID

    # "--operation-mode=historical-balances" is not available for nodes,
    # since << validator cannot be a full archive node >>,
    # but we attempt to set the "deep-history" mode as follows:
    data["DbLookupExtensions"]["Enabled"] = True
    data["GeneralSettings"]["StartInEpochEnabled"] = False
    data["StateTriesConfig"]["AccountsStatePruningEnabled"] = False
    data["StoragePruning"]["ObserverCleanOldEpochsData"] = False
    data["StoragePruning"]["AccountsTrieCleanOldEpochsData"] = False

    # Some time after the release of Supernova, we should drop this custom (and somehow cumbersome) logic.
    if supernova_activation_epoch is None:
        # Before Supernova (as software version, not as "era after activation"),
        # we alter epoch duration by adjusting "RoundsPerEpoch" and "MinRoundsBetweenEpochs" in section "EpochStartConfig".
        # In a Supernova-aware node configuration, these entries do not exist anymore (see "ChainParametersByEpoch").
        epoch_start_config: ConfigDict = dict()
        epoch_start_config["RoundsPerEpoch"] = config.general.rounds_per_epoch
        epoch_start_config["MinRoundsBetweenEpochs"] = int(
            config.general.rounds_per_epoch / ROUNDS_PER_EPOCH_TO_MIN_ROUNDS_BETWEEN_EPOCHS_RATIO
        )

        data["EpochStartConfig"].update(epoch_start_config)

    data["WebServerAntiflood"]["VmQueryDelayAfterStartInSec"] = 30

    # Always use the latest VM
    data["VirtualMachine"]["Execution"]["WasmVMVersions"] = [{"StartEpoch": 0, "Version": "*"}]
    data["VirtualMachine"]["Querying"]["WasmVMVersions"] = [{"StartEpoch": 0, "Version": "*"}]

    # Adjust "ChainParametersByEpoch"
    chain_parameters_by_epoch = data["GeneralSettings"].get("ChainParametersByEpoch", [])

    for item in chain_parameters_by_epoch:
        enable_epoch = item["EnableEpoch"]

        if supernova_activation_epoch and enable_epoch >= supernova_activation_epoch:
            item["RoundDuration"] = config.general.round_duration_milliseconds_in_supernova
            item["RoundsPerEpoch"] = config.general.rounds_per_epoch_in_supernova
            item["MinRoundsBetweenEpochs"] = int(
                config.general.rounds_per_epoch_in_supernova / ROUNDS_PER_EPOCH_TO_MIN_ROUNDS_BETWEEN_EPOCHS_RATIO
            )
        else:
            item["RoundDuration"] = config.general.round_duration_milliseconds
            item["RoundsPerEpoch"] = config.general.rounds_per_epoch
            item["MinRoundsBetweenEpochs"] = int(
                config.general.rounds_per_epoch / ROUNDS_PER_EPOCH_TO_MIN_ROUNDS_BETWEEN_EPOCHS_RATIO
            )

        item["ShardConsensusGroupSize"] = config.shards.consensus_size
        item["ShardMinNumNodes"] = config.shards.num_validators_per_shard
        item["MetachainConsensusGroupSize"] = config.metashard.consensus_size
        item["MetachainMinNumNodes"] = config.metashard.num_validators


def patch_api(data: ConfigDict, config: ConfigRoot):
    routes = data["APIPackages"]["transaction"]["Routes"]
    for route in routes:
        route["Open"] = True


def patch_enable_epochs(data: ConfigDict, config: ConfigRoot):
    enable_epochs = data["EnableEpochs"]
    enable_epochs["AheadOfTimeGasUsageEnableEpoch"] = 0
    enable_epochs["GasPriceModifierEnableEpoch"] = 0
    enable_epochs["RepairCallbackEnableEpoch"] = 0
    enable_epochs["ReturnDataToLastTransferEnableEpoch"] = 0
    enable_epochs["SenderInOutTransferEnableEpoch"] = 0
    enable_epochs["ESDTEnableEpoch"] = 0
    enable_epochs["IncrementSCRNonceInMultiTransferEnableEpoch"] = 0
    enable_epochs["ESDTMultiTransferEnableEpoch"] = 0
    enable_epochs["GlobalMintBurnDisableEpoch"] = 0
    enable_epochs["ESDTTransferRoleEnableEpoch"] = 0
    enable_epochs["MultiESDTTransferFixOnCallBackOnEnableEpoch"] = 0
    enable_epochs["ESDTNFTCreateOnMultiShard"] = 0
    enable_epochs["MetaESDTSetEnableEpoch"] = 0
    enable_epochs["DelegationManagerEnableEpoch"] = 0

    # Adjust "MaxNumNodes":
    max_nodes_change_enable_epoch = enable_epochs["MaxNodesChangeEnableEpoch"]
    last_entry = max_nodes_change_enable_epoch[-1]
    penultimate_entry = max_nodes_change_enable_epoch[-2]
    last_entry["MaxNumNodes"] = (
        penultimate_entry["MaxNumNodes"] - (config.shards.num_shards + 1) * penultimate_entry["NodesToShufflePerShard"]
    )
