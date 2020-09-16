import logging
import os
import shutil

import erdpy.utils as utils
from erdpy import myprocess
from erdpy.dependencies.install import install_module
from erdpy.testnet import genesis_json, nodes_setup_json, wallets
from erdpy.testnet.config import TestnetConfiguration

logger = logging.getLogger("testnet")

DEPENDENCY_KEYS = ["elrond_config_testnet", "elrond_go", "elrond_proxy_go"]


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

    # Validators and Observers
    copy_config_to_nodes(testnet_config)
    copy_validator_keys(testnet_config)

    patch_nodes_p2p_config(
        testnet_config,
        testnet_config.validator_config_folders(),
        testnet_config.networking['port_first_validator'],
    )
    patch_nodes_p2p_config(
        testnet_config,
        testnet_config.observer_config_folders(),
        testnet_config.networking['port_first_observer'],
    )
    overwrite_nodes_setup(
        testnet_config,
        testnet_config.validator_config_folders(),
    )
    overwrite_nodes_setup(
        testnet_config,
        testnet_config.observer_config_folders(),
    )
    overwrite_genesis_file(
        testnet_config,
        testnet_config.validator_config_folders()
    )
    overwrite_genesis_file(
        testnet_config,
        testnet_config.observer_config_folders()
    )

    # Seed node
    copy_config_to_seednode(testnet_config)
    patch_seednode_config(testnet_config)

    # Proxy
    copy_config_to_proxy(testnet_config)
    write_observers_list_to_proxy_config(testnet_config)

    build_binaries(testnet_config)


def clean(args):
    testnet_config = TestnetConfiguration.from_file(args.configfile)
    logger.info('testnet folder is %s', testnet_config.root())

    shutil.rmtree(testnet_config.root())


def create_folders(testnet_config: TestnetConfiguration):
    makefolder(testnet_config.seednode_folder())

    if testnet_config.features['proxy'] is True:
        folder = testnet_config.proxy_folder()
        makefolder(folder)
        makefolder(folder / 'config')

    for folder in testnet_config.all_nodes_folders():
        makefolder(folder)


def copy_config_to_nodes(testnet_config: TestnetConfiguration):
    config_source = testnet_config.node_config_source()
    for node_config in testnet_config.all_nodes_config_folders():
        shutil.copytree(
            config_source,
            node_config)


def copy_validator_keys(testnet_config: TestnetConfiguration):
    for index, validator in enumerate(testnet_config.validators()):
        shutil.copy(wallets.get_validator_key_file(index), validator.key_file_path())

    # Currently, observers require validator PEM files as well
    for index, observer in enumerate(testnet_config.observers()):
        shutil.copy(wallets.get_observer_key_file(index), observer.key_file_path())


def copy_config_to_seednode(testnet_config: TestnetConfiguration):
    config_source = testnet_config.node_source() / 'cmd' / 'seednode' / 'config'
    seednode_config = testnet_config.seednode_config_folder()
    makefolder(seednode_config)
    shutil.copy(config_source / 'p2p.toml', seednode_config / 'p2p.toml')
    shutil.copy(config_source / 'config.toml', seednode_config / 'config.toml')


def patch_seednode_config(testnet_config: TestnetConfiguration):
    seednode_config = testnet_config.seednode_config_folder()
    seednode_config_file = seednode_config / 'p2p.toml'

    data = utils.read_toml_file(seednode_config_file)
    data['Node']['Port'] = str(testnet_config.networking['port_seednode'])
    utils.write_toml_file(seednode_config_file, data)


def patch_nodes_p2p_config(testnet_config: TestnetConfiguration, nodes_config_folders, port_first):
    for index, config_folder in enumerate(nodes_config_folders):
        # Edit the p2p.toml file
        config = config_folder / 'p2p.toml'
        data = utils.read_toml_file(config)
        data['Node']['Port'] = str(port_first + index)
        data['KadDhtPeerDiscovery']['InitialPeerList'] = [
            testnet_config.seednode_address()
        ]
        utils.write_toml_file(config, data)


def overwrite_nodes_setup(testnet_config: TestnetConfiguration, nodes_config_folders):
    nodes_setup = nodes_setup_json.build(testnet_config)

    for index, config_folder in enumerate(nodes_config_folders):
        config = config_folder / 'nodesSetup.json'
        utils.write_json_file(str(config), nodes_setup)


def overwrite_genesis_file(testnet_config: TestnetConfiguration, nodes_config_folders):
    genesis = genesis_json.build(testnet_config)

    for index, config_folder in enumerate(nodes_config_folders):
        config = config_folder / 'genesis.json'
        utils.write_json_file(str(config), genesis)


def copy_config_to_proxy(testnet_config: TestnetConfiguration):
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


def write_observers_list_to_proxy_config(testnet_config: TestnetConfiguration):
    proxy_config_file = testnet_config.proxy_config_folder() / 'config.toml'
    observers = testnet_config.observer_addresses_sharded_for_proxy_config()
    data = utils.read_toml_file(proxy_config_file)
    data['Observers'] = observers
    data['GeneralSettings']['ServerPort'] = testnet_config.networking['port_proxy']
    utils.write_toml_file(proxy_config_file, data)


def makefolder(path):
    path.mkdir(parents=True, exist_ok=True)


def build_binaries(testnet_config: TestnetConfiguration):
    logger.info("Building seednode...")
    seednode_folder = testnet_config.node_source() / "cmd" / "seednode"
    myprocess.run_process(['go', 'build'], cwd=seednode_folder)

    logger.info("Building node...")
    node_folder = testnet_config.node_source() / "cmd" / "node"
    myprocess.run_process(['go', 'build'], cwd=node_folder)

    logger.info("Building arwen...")
    node_folder_root = testnet_config.node_source()
    env = dict(os.environ)
    env["ARWEN_PATH"] = node_folder
    myprocess.run_process(['make', 'arwen'], cwd=node_folder_root, env=env)

    logger.info("Building proxy...")
    proxy_folder = testnet_config.proxy_source() / "cmd" / "proxy"
    myprocess.run_process(['go', 'build'], cwd=proxy_folder)

    # Now copy the binaries to the testnet folder
    shutil.copy(seednode_folder / "seednode", testnet_config.seednode_folder())

    for destination in testnet_config.all_nodes_folders():
        shutil.copy(node_folder / "node", destination)
        shutil.copy(node_folder / "arwen", destination)

    shutil.copy(proxy_folder / "proxy", testnet_config.proxy_folder())
