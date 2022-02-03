import os
import sys

from pathlib import Path

import erdpy.config
from erdpy import workstation
from erdpy.testnet import config

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
        'elrond_go': '{ELRONDSDK}/bar',
        'elrond_proxy_go': '{ELRONDSDK}/foobar',
        'testnet': '/some/where/mytestnet',
    }

    sdk_folder = workstation.get_tools_folder()
    node_folder = erdpy.config.get_dependency_parent_directory('elrond_go')
    (node_folder / 'v1.2.3').mkdir(parents=True, exist_ok=True)

    proxy_folder = erdpy.config.get_dependency_parent_directory('elrond_proxy_go')
    (proxy_folder / 'v2.3.4').mkdir(parents=True, exist_ok=True)

    testnet_config = config.TestnetConfiguration(data)
    assert testnet_config.folders["elrond_go"] == sdk_folder / "bar"
    assert testnet_config.folders["elrond_proxy_go"] == sdk_folder / "foobar"
    assert testnet_config.folders["testnet"] == Path("/some/where/mytestnet")
