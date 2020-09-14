import sys
import os
from pathlib import Path

sys.path = [os.getcwd() + '/..'] + sys.path

from erdpy.testnet import configuration


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
        'nodes_start_time': 60,
        'seednode_start_time': 5,
    }

    expected_merged = dict()
    expected_merged['metashard'] = {
        'consensus_size': 1,
        'metashardID': 4294967295,
        'observers': 0,
        'validators': 4,
    }
    expected_merged['timing'] = {
        'genesis_delay': 30,
        'nodes_start_time': 60,
        'seednode_start_time': 5,
    }
    expected_merged['networking'] = {
        'port_proxy': 7950,
        'port_seednode_port': 9999,
        'somekey': 'somestring',
    }

    result_merged = configuration.merge_configs(left, right)
    assert expected_merged == result_merged


def test_init():
    config = dict()
    config['folders'] = {
        'elrond_config_mainnet': '{ELRONDSDK}/elrond-config-mainnet',
        'elrond_go': '{ELRONDSDK}/elrond-go',
        'elrond_proxy_go': '{ELRONDSDK}/elrond-proxy-go',
        'testnet': '{ELRONDSDK}/testnet',
    }

    testnet_config = configuration.TestnetConfiguration(config)
    print(testnet_config.config)
