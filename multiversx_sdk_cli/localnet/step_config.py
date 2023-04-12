import logging
import os
import shutil
from os import path
from pathlib import Path
from typing import Any, List

import multiversx_sdk_cli.utils as utils
from multiversx_sdk_cli.localnet import (genesis_json,
                                         genesis_smart_contracts_json,
                                         node_config_toml, nodes_setup_json,
                                         p2p_toml, wallets)
from multiversx_sdk_cli.localnet.config import ConfigRoot

logger = logging.getLogger("localnet")


def configure(args: Any):
    config = ConfigRoot.from_file(args.configfile)
    logger.info("localnet folder is %s", config.root())

    create_folders(config)

    # Validators and Observers
    copy_config_to_nodes(config)
    copy_validator_keys(config)
    patch_node_config(config)

    patch_nodes_p2p_config(
        config,
        config.validator_config_folders(),
        config.networking.port_first_validator,
    )
    patch_nodes_p2p_config(
        config,
        config.observer_config_folders(),
        config.networking.port_first_observer,
    )
    overwrite_nodes_setup(
        config,
        config.validator_config_folders(),
    )
    overwrite_nodes_setup(
        config,
        config.observer_config_folders(),
    )
    overwrite_genesis_file(
        config,
        config.validator_config_folders()
    )
    overwrite_genesis_file(
        config,
        config.observer_config_folders()
    )

    # Seed node
    copy_config_to_seednode(config)
    patch_seednode_p2p_config(config)
    copy_seednode_p2p_key(config)

    # Proxy
    copy_config_to_proxy(config)
    patch_proxy_config(config)

    copy_binaries_into_localnet_workspace(config)


def create_folders(config: ConfigRoot):
    makefolder(config.seednode_folder())

    folder = config.proxy_folder()
    makefolder(folder)
    makefolder(folder / 'config')

    for folder in config.all_nodes_folders():
        makefolder(folder)


def copy_config_to_nodes(config: ConfigRoot):
    config_prototype = config.software.get_node_config_folder()
    for node_config in config.all_nodes_config_folders():
        shutil.copytree(config_prototype, node_config)


def copy_validator_keys(config: ConfigRoot):
    for index, validator in enumerate(config.validators()):
        shutil.copy(wallets.get_validator_key_file(index), validator.key_file_path())

    # Currently, observers require validator PEM files as well (we have to adjust this and use --no-key parameter)
    for index, observer in enumerate(config.observers()):
        shutil.copy(wallets.get_observer_key_file(index), observer.key_file_path())


def patch_node_config(config: ConfigRoot):
    for node_config in config.all_nodes_config_folders():
        node_config_file = node_config / 'config.toml'
        data = utils.read_toml_file(node_config_file)
        node_config_toml.patch_config(data, config)
        utils.write_toml_file(node_config_file, data)

        api_config_file = node_config / 'api.toml'
        data = utils.read_toml_file(api_config_file)
        node_config_toml.patch_api(data, config)
        utils.write_toml_file(api_config_file, data)

        enable_epochs_config_file = node_config / 'enableEpochs.toml'
        data = utils.read_toml_file(enable_epochs_config_file)
        node_config_toml.patch_enable_epochs(data, config)
        utils.write_toml_file(enable_epochs_config_file, data)

        genesis_smart_contracts_file = node_config / 'genesisSmartContracts.json'
        data = utils.read_json_file(genesis_smart_contracts_file)
        genesis_smart_contracts_json.patch(data, config)
        utils.write_json_file(genesis_smart_contracts_file, data)


def copy_config_to_seednode(config: ConfigRoot):
    config_source = config.software.get_seednode_config_folder()
    seednode_config = config.seednode_config_folder()
    makefolder(seednode_config)
    shutil.copy(config_source / 'p2p.toml', seednode_config / 'p2p.toml')
    shutil.copy(config_source / 'config.toml', seednode_config / 'config.toml')


def patch_seednode_p2p_config(config: ConfigRoot):
    seednode_config = config.seednode_config_folder()
    seednode_config_file = seednode_config / 'p2p.toml'

    data = utils.read_toml_file(seednode_config_file)
    p2p_toml.patch_for_seednode(data, config)
    utils.write_toml_file(seednode_config_file, data)


def copy_seednode_p2p_key(config: ConfigRoot):
    p2p_key_path = Path(__file__).parent / "seednode_p2pKey.pem"
    shutil.copy(p2p_key_path, config.seednode_config_folder() / "p2pKey.pem")


def patch_nodes_p2p_config(config: ConfigRoot, nodes_config_folders: List[Path], port_first: int):
    for index, config_folder in enumerate(nodes_config_folders):
        config_file = config_folder / 'p2p.toml'
        data = utils.read_toml_file(config_file)
        p2p_toml.patch(data, config, index, port_first)
        utils.write_toml_file(config_file, data)


def overwrite_nodes_setup(config: ConfigRoot, nodes_config_folders: List[Path]):
    nodes_setup = nodes_setup_json.build(config)

    for _, config_folder in enumerate(nodes_config_folders):
        utils.write_json_file(config_folder / 'nodesSetup.json', nodes_setup)


def overwrite_genesis_file(config: ConfigRoot, nodes_config_folders: List[Path]):
    genesis = genesis_json.build(config)

    for _, config_folder in enumerate(nodes_config_folders):
        utils.write_json_file(config_folder / 'genesis.json', genesis)


def copy_config_to_proxy(config: ConfigRoot):
    config_prototype = config.software.get_proxy_config_folder()
    proxy_config = config.proxy_config_folder()
    makefolder(proxy_config)

    shutil.copy(
        config_prototype / 'config.toml',
        proxy_config)

    shutil.copytree(
        config_prototype / 'apiConfig',
        proxy_config / 'apiConfig')

    shutil.copy(
        config_prototype / 'external.toml',
        proxy_config)


def patch_proxy_config(config: ConfigRoot):
    proxy_config_file = config.proxy_config_folder() / 'config.toml'
    nodes = config.api_addresses_sharded_for_proxy_config()
    data = utils.read_toml_file(proxy_config_file)
    data['Observers'] = nodes
    data['FullHistoryNodes'] = nodes
    data['GeneralSettings']['ServerPort'] = config.networking.port_proxy
    utils.write_toml_file(proxy_config_file, data)

    api_config_file = path.join(config.proxy_config_folder(), 'apiConfig', 'v1_0.toml')
    data = utils.read_toml_file(api_config_file)
    routes = data['APIPackages']['transaction']['Routes']
    for route in routes:
        route["Open"] = True
    utils.write_toml_file(api_config_file, data)


def makefolder(path_where_to_make_folder: Path):
    path_where_to_make_folder.mkdir(parents=True, exist_ok=True)


def copy_binaries_into_localnet_workspace(config: ConfigRoot):
    [node_cmd, seednode_cmd, proxy_cmd] = config.software.get_binaries_parents()

    for destination in config.all_nodes_folders():
        shutil.copy(node_cmd / "node", destination)
        copy_libraries(node_cmd, destination)

    shutil.copy(seednode_cmd / "seednode", config.seednode_folder())
    copy_libraries(seednode_cmd, config.seednode_folder())

    shutil.copy(proxy_cmd / "proxy", config.proxy_folder())
    copy_libraries(proxy_cmd, config.proxy_folder())


def copy_libraries(source: Path, destination: Path):
    libraries: List[Path] = list(source.glob("*.dylib")) + list(source.glob("*.so"))

    for library in libraries:
        logger.info(f"Copying {library} to {destination}")

        shutil.copy(library, destination)
        os.chmod(destination / library.name, 0o755)
