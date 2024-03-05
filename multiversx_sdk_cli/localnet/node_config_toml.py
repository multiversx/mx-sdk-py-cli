from typing import Any, Dict

from multiversx_sdk_cli.localnet.config_root import ConfigRoot
from multiversx_sdk_cli.localnet.nodes_setup_json import CHAIN_ID

ConfigDict = Dict[str, Any]


def patch_config(data: ConfigDict, config: ConfigRoot):
    data['DbLookupExtensions']['Enabled'] = True

    general_settings: ConfigDict = dict()
    general_settings['ChainID'] = CHAIN_ID
    general_settings['StartInEpochEnabled'] = False
    general_settings['SetGuardianEpochsDelay'] = 1

    data['GeneralSettings'].update(general_settings)

    # Make epochs shorter
    epoch_start_config: ConfigDict = dict()
    epoch_start_config['RoundsPerEpoch'] = config.general.rounds_per_epoch
    epoch_start_config['MinRoundsBetweenEpochs'] = int(config.general.rounds_per_epoch / 4)

    data['EpochStartConfig'].update(epoch_start_config)

    # Always use the latest VM
    virtual_machine: Dict[str, Any] = dict()
    virtual_machine['Execution'] = dict()
    virtual_machine['Execution']['WasmVMVersions'] = [{'StartEpoch': 0, 'Version': '*'}]
    virtual_machine['Querying'] = dict()
    virtual_machine['Querying']['NumConcurrentVMs'] = 1
    virtual_machine['Querying']['WasmVMVersions'] = [{'StartEpoch': 0, 'Version': '*'}]

    data['VirtualMachine'].update(virtual_machine)


def patch_api(data: ConfigDict, config: ConfigRoot):
    routes = data['APIPackages']['transaction']['Routes']
    for route in routes:
        route['Open'] = True


def patch_enable_epochs(data: ConfigDict, config: ConfigRoot):
    pass
