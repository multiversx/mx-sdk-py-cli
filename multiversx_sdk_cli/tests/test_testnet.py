import os
import sys
from typing import Any, Dict

from multiversx_sdk_cli.localnet.config_root import ConfigRoot
from multiversx_sdk_cli.localnet.config_software import SoftwareResolution

sys.path = [os.getcwd() + "/.."] + sys.path


def test_override_config():
    config = ConfigRoot()

    # Check a few default values
    assert config.general.rounds_per_epoch == 100
    assert config.general.round_duration_milliseconds == 6000
    assert config.metashard.consensus_size == 1
    assert config.networking.port_proxy == 7950
    assert config.software.mx_chain_go.resolution == SoftwareResolution.Remote
    assert config.software.mx_chain_go.archive_url == "https://github.com/multiversx/mx-chain-go/archive/refs/heads/master.zip"

    # Now partly override the config
    config_patch: Dict[str, Any] = dict()
    config_patch["general"] = {
        "rounds_per_epoch": 200,
        "round_duration_milliseconds": 4000,
    }
    config_patch["metashard"] = {
        "consensus_size": 2,
    }
    config_patch["networking"] = {
        "port_proxy": 7951,
    }
    config_patch["software"] = {
        "mx_chain_go": {
            "archive_url": "https://github.com/multiversx/mx-chain-go/archive/refs/tags/v1.5.1.zip"
        }
    }

    config.override(config_patch)

    # Check the overridden values
    assert config.general.rounds_per_epoch == 200
    assert config.general.round_duration_milliseconds == 4000
    assert config.metashard.consensus_size == 2
    assert config.networking.port_proxy == 7951
    assert config.software.mx_chain_go.resolution == SoftwareResolution.Remote
    assert config.software.mx_chain_go.archive_url == "https://github.com/multiversx/mx-chain-go/archive/refs/tags/v1.5.1.zip"
