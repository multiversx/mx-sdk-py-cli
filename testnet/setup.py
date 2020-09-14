import os
import logging
from erdpy import myprocess
import shutil

import erdpy.utils as utils
from erdpy.testnet.TestnetConfiguration import TestnetConfiguration

logger = logging.getLogger("testnet")

from erdpy.dependencies.install import install_module

DEPENDENCY_KEYS = ["elrond_config_mainnet", "elrond_go", "elrond_proxy_go"]

def install_dependencies():
    # TODO verify if Go compiler is available, and has a recent version
    for key in DEPENDENCY_KEYS:
        name: str = key
        tag: str = ""
        overwrite: bool = True
        install_module(name, tag, overwrite)


def configure(args):
    testnet_config = TestnetConfiguration.from_file(args.configfile)
    logger.info('testnet folder is %s', testnet_config.root())

    create_folders(testnet_config)
    copy_config_to_nodes(testnet_config)

    generate_validator_keys(testnet_config)
    copy_validator_keys(testnet_config)

    update_nodes_config(
        testnet_config,
        testnet_config.validator_config_folders(),
        testnet_config.networking['port_first_validator'],
    )

    update_nodes_config(
        testnet_config,
        testnet_config.observer_config_folders(),
        testnet_config.networking['port_first_observer'],
    )

    write_validator_keys_as_initial_nodes(testnet_config)

    copy_config_to_seednode(testnet_config)
    write_seednode_port(testnet_config)

    copy_config_to_proxy(testnet_config)
    write_observers_list_to_proxy_config(testnet_config)


def clean(args):
    testnet_config = TestnetConfiguration.from_file(args.configfile)
    logger.info('testnet folder is %s', testnet_config.root())

    shutil.rmtree(testnet_config.root())


def create_folders(testnet_config):
    makefolder(testnet_config.seednode_folder())

    if testnet_config.features['proxy'] is True:
        folder = testnet_config.proxy_folder()
        makefolder(folder)
        makefolder(folder / 'config')

    for folder in testnet_config.all_nodes_folders():
        makefolder(folder)


def copy_config_to_nodes(testnet_config):
    config_source = testnet_config.node_config_source()
    for node_config in testnet_config.all_nodes_config_folders():
        shutil.copytree(
            config_source,
            node_config,
            dirs_exist_ok=True)


def generate_validator_keys(testnet_config):
    keygen_folder = testnet_config.keygenerator_folder()
    prev_cwd = os.getcwd()
    os.chdir(keygen_folder)
    myprocess.run_process(['go', 'build'])
    myprocess.run_process([
        './keygenerator',
        '--key-type', 'validator',
        '--num-keys', str(testnet_config.num_all_validators()),
    ])
    os.chdir(prev_cwd)


def copy_validator_keys(testnet_config):
    validator_key_files = testnet_config.validator_key_files()
    for index, key_file in enumerate(validator_key_files):
        shutil.copy(
            testnet_config.keygenerator_key_file(index),
            key_file)


def copy_config_to_seednode(testnet_config):
    config_source = testnet_config.node_config_source()
    seednode_config = testnet_config.seednode_config_folder()
    shutil.copytree(
        config_source,
        seednode_config,
        dirs_exist_ok=True)


def write_seednode_port(testnet_config):
    seednode_config = testnet_config.seednode_config_folder()
    seednode_config_file = seednode_config / 'p2p.toml'

    data = utils.read_toml_file(seednode_config_file)
    data['Node']['Port'] = testnet_config.networking['port_seednode']
    utils.write_toml_file(seednode_config_file, data)


def update_nodes_config(testnet_config, nodes_config_folders, port_first):
    for index, config_folder in enumerate(nodes_config_folders):
        # Edit the p2p.toml file
        config = config_folder / 'p2p.toml'
        data = utils.read_toml_file(config)
        data['Node']['Port'] = port_first + index
        data['KadDhtPeerDiscovery']['InitialPeerList'] = [
            testnet_config.seednode_address()
        ]
        utils.write_toml_file(config, data)

        # Edit the nodesSetup.json file
        config = config_folder / 'nodesSetup.json'
        data = utils.read_json_file(str(config))
        data["startTime"] = testnet_config.genesis_time()
        data["minTransactionVersion"] = "1"
        data["chainID"] = "local-testnet"
        data["consensusGroupSize"] = testnet_config.shards['consensus_size']
        data["metaChainConsensusGroupSize"] = testnet_config.metashard['consensus_size']
        data["metaChainMinNodes"] = testnet_config.metashard['validators']
        utils.write_json_file(str(config), data)


def write_validator_keys_as_initial_nodes(testnet_config):
    # TODO how to transform the validatoyKey.pem files into the initialNodes
    # entries in every node's nodesSetup.json?
    logger.warn("nodesSetup.json not updated with initialNodes")
    pass


def copy_config_to_proxy(testnet_config):
    proxy_config_source = testnet_config.proxy_config_source()
    node_config_source = testnet_config.node_config_source()
    proxy_config = testnet_config.proxy_config_folder()
    makefolder(proxy_config)

    shutil.copy(
        proxy_config_source / 'config.toml',
        proxy_config)

    shutil.copy(
        proxy_config_source / 'external.toml',
        proxy_config)

    shutil.copy(
        node_config_source / 'economics.toml',
        proxy_config)


def write_observers_list_to_proxy_config(testnet_config):
    proxy_config_file = testnet_config.proxy_config_folder() / 'config.toml'
    observers = testnet_config.observer_addresses_sharded_for_proxy_config()
    data = utils.read_toml_file(proxy_config_file)
    data['Observers'] = observers
    data['GeneralSettings']['ServerPort'] = testnet_config.networking['port_proxy']
    utils.write_toml_file(proxy_config_file, data)


def makefolder(path):
    path.mkdir(parents=True, exist_ok=True)
