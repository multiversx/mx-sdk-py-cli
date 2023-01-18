import os
import sys
from pathlib import Path

import multiversx_sdk_cli.config
from multiversx_sdk_cli import workstation
from multiversx_sdk_cli.testnet import config

sys.path = [os.getcwd() + '/..'] + sys.path


def test_merge_configs():
    left = dict()
    left['networking'] = {
        'port_proxy': 7950,
        'port_seednode_port': 9999,
        'somekey': 'somestring',
    }
    left['metashard'] = {
        'metashardID': 4294967295,
        'observers': 0,
        'validators': 1,
    }

    right = dict()
    right['metashard'] = {
        'consensus_size': 1,
        'metashardID': 4294967295,
        'validators': 4,
    }
    right['timing'] = {
        'genesis_delay': 30,
    }

    expected_merged = dict()
    expected_merged['metashard'] = {
        'consensus_size': 1,
        'metashardID': 4294967295,
        'observers': 0,
        'validators': 4,
    }
    expected_merged['timing'] = {
        'genesis_delay': 30
    }
    expected_merged['networking'] = {
        'port_proxy': 7950,
        'port_seednode_port': 9999,
        'somekey': 'somestring',
    }

    result_merged = config.merge_configs(left, right)
    assert expected_merged == result_merged


def test_init():
    data = dict()
    data['folders'] = {
        'mx_chain_go': '{MULTIVERSX_SDK}/bar',
        'mx_chain_proxy_go': '{MULTIVERSX_SDK}/foobar',
        'testnet': '/some/where/mytestnet',
    }

    sdk_folder = workstation.get_tools_folder()
    node_folder = multiversx_sdk_cli.config.get_dependency_parent_directory('mx_chain_go')
    (node_folder / 'v1.2.3').mkdir(parents=True, exist_ok=True)

    proxy_folder = multiversx_sdk_cli.config.get_dependency_parent_directory('mx_chain_proxy_go')
    (proxy_folder / 'v2.3.4').mkdir(parents=True, exist_ok=True)

    testnet_config = config.TestnetConfiguration(data)
    assert testnet_config.folders["mx_chain_go"] == sdk_folder / "bar"
    assert testnet_config.folders["mx_chain_proxy_go"] == sdk_folder / "foobar"
    assert testnet_config.folders["testnet"] == Path("/some/where/mytestnet")
