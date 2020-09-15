import itertools
import logging
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

import erdpy.config
import erdpy.utils as utils
from erdpy import workstation

logger = logging.getLogger("testnet")

ConfigurationType = Dict[str, Dict[str, Any]]


class TestnetConfiguration:

    def __init__(self, config):
        self.config = config

        sdk_folder = workstation.get_tools_folder()

        for key, path in self.config['folders'].items():
            path = path.replace('{ELRONDSDK}', str(sdk_folder))

            default_tag = erdpy.config.get_dependency_tag(key)
            path = path.replace('{TAG}', default_tag)

            # If the user has not specified a custom source repository, the
            # ones provided by the SDK will be used, which are downloaded as
            # tar.gz files from GitHub. Due to how the name of the archive is
            # built by GitHub, the folder will contain the tag in two variants:
            # with the 'v' prefix (e.g. "v1.1.0"), but also without (e.g.
            # "1.1.0"), hence the need for {NOvTAG}.
            default_no_v_tag = default_tag.replace('v', '')
            path = path.replace('{NOvTAG}', default_no_v_tag)

            self.config['folders'][key] = Path(path).expanduser()

        if 'testnet' not in self.config['folders']:
            self.config['folders']['testnet'] = Path().absolute() / 'testnet'

        self.__dict__.update(self.config)

    @classmethod
    def from_file(cls, filename):
        """
        If no filename is specified, try to load testnet.toml from the current
        directory, if there is any, and merge it with the SDK-level testnet
        config. Otherwise, load the SDK-level testnet config. If that one is
        missing as well, generate it from hard-coded defaults.
        """

        local_config = cls.get_local_config(filename)
        sdk_testnet_config = cls.get_sdk_testnet_config()
        final_config = merge_configs(sdk_testnet_config, local_config)

        return cls(final_config)

    @classmethod
    def from_sdk_testnet_config(cls):
        config = cls.get_sdk_testnet_config()
        return cls(config)

    @classmethod
    def from_default_config(cls):
        return cls(cls.default())

    @classmethod
    def get_local_config(cls, filename):
        if filename is None or filename == '':
            filename = Path() / "testnet.toml"
            if not filename.exists():
                return dict()

        logger.info('using local testnet config from %s', filename)
        return utils.read_toml_file(filename)

    @classmethod
    def get_sdk_testnet_config(cls):
        default = cls.default()
        filename = workstation.get_tools_folder() / "testnet.toml"
        logger.info('sdk_testnet_config filename %s', filename)
        if not filename.exists():
            logger.info('writing sdk_testnet_config from defaults')
            utils.write_toml_file(str(filename), default)
            return default
        sdk_testnet_config = utils.read_toml_file(filename)
        return merge_configs(default, sdk_testnet_config)

    def node_config_source(self):
        return self.folders['elrond_config_testnet']

    def node_source(self):
        return self.folders['elrond_go']

    def proxy_source(self):
        return self.folders['elrond_proxy_go']

    def proxy_config_source(self):
        return self.folders['elrond_proxy_go'] / 'cmd' / 'proxy' / 'config'

    def keygenerator_folder(self):
        return self.node_source() / 'cmd' / 'keygenerator'

    def validator_key_files(self):
        for config_folder in self.validator_config_folders():
            yield config_folder / 'validatorKey.pem'

    def keygenerator_key_file(self, index):
        index = str(index)
        return self.keygenerator_folder() / ('node-' + index) / 'validatorKey.pem'

    def root(self):
        return self.folders['testnet']

    def genesis_time(self):
        return int(time.time()) + int(self.timing['genesis_delay'])

    def seednode_folder(self):
        testnet = self.root()
        return testnet / 'seednode'

    def seednode_config_folder(self):
        return self.seednode_folder() / 'config'

    def seednode_address(self):
        host = self.networking['host']
        port = self.networking['port_seednode']
        identifier = self.networking['p2p_id_seednode']
        return f"/ip4/{host}/tcp/{port}/p2p/{identifier}"

    def proxy_folder(self):
        testnet = self.root()
        return testnet / 'proxy'

    def proxy_config_folder(self):
        return self.proxy_folder() / 'config'

    def num_all_nodes(self):
        return self.num_all_validators() + self.num_all_observers()

    def num_all_validators(self):
        count = (
            self.shards['count'] * self.shards['validators_per_shard'] + self.metashard['validators']
        )
        return count

    def num_all_observers(self):
        count = (
            self.shards['count'] * self.shards['observers_per_shard'] + self.metashard['observers']
        )
        return count

    def num_shards(self):
        return self.shards['count']

    def num_observers_per_shard(self):
        return self.shards['observers_per_shard']

    def all_nodes_folders(self):
        return itertools.chain(
            self.validator_folders(),
            self.observer_folders(),
        )

    def all_nodes_config_folders(self):
        return itertools.chain(
            self.validator_config_folders(),
            self.observer_config_folders(),
        )

    def validator_folders(self):
        testnet = self.root()
        for i in range(self.num_all_validators()):
            yield testnet / 'validator{:02}'.format(i)

    def validator_config_folder(self, validator_index):
        return self.root() / 'validator{:02}'.format(validator_index) / 'config'

    def validator_config_folders(self):
        for folder in self.validator_folders():
            yield folder / 'config'

    def observer_config_folders(self):
        for folder in self.observer_folders():
            yield folder / 'config'

    def observer_folders(self):
        testnet = self.root()
        for i in range(self.num_all_observers()):
            yield testnet / 'observer{:02}'.format(i)

    def observer_addresses(self):
        host = self.networking['host']
        first_port = self.networking['port_first_observer']
        for port in range(self.num_all_observers()):
            port = first_port + port
            yield f"http://{host}:{port}"

    def observer_addresses_sharded(self):
        sharded_observers = defaultdict(list)
        observers_per_shard = self.num_observers_per_shard()
        num_shards = self.num_shards()
        shard = 0
        for i, address in enumerate(self.observer_addresses()):
            if shard < num_shards:
                if i > 0 and i % observers_per_shard == 0:
                    shard += 1
                    if shard == num_shards:
                        shard = self.metashard['metashardID']

            sharded_observers[shard].append(address)

        return sharded_observers

    def observer_addresses_sharded_for_proxy_config(self):
        observers = list()
        for shard, addresses in self.observer_addresses_sharded().items():
            for address in addresses:
                observers.append({
                    'ShardId': shard,
                    'Address': address
                })
        return observers

    @classmethod
    def default(cls):
        config = dict()
        config['features'] = {
            'loglevel': '*:INFO',
            'proxy': True,
        }
        config['folders'] = {
            'elrond_config_testnet':
                '{ELRONDSDK}/elrond_config_testnet/{TAG}/elrond-config-testnet-{NOvTAG}',
            'elrond_go':
                '{ELRONDSDK}/elrond_go/{TAG}/elrond-go-{NOvTAG}',
            'elrond_proxy_go':
                '{ELRONDSDK}/elrond_proxy_go/{TAG}/elrond-proxy-go-{NOvTAG}',
        }
        config['metashard'] = {
            'consensus_size': 1,
            'metashardID': 4294967295,
            'observers': 1,
            'validators': 1,
        }
        config['networking'] = {
            'host': '127.0.0.1',
            'port_seednode': 9999,
            'p2p_id_seednode': '16Uiu2HAkw5SNNtSvH1zJiQ6Gc3WoGNSxiyNueRKe6fuAuh57G3Bk',
            'port_proxy': 7950,
            'port_first_observer': 21100,
            'port_first_observer_rest_api': 10000,
            'port_first_validator': 21500,
            'port_first_validator_rest_api': 21500,
        }
        config['shards'] = {
            'consensus_size': 1,
            'count': 1,
            'observers_per_shard': 1,
            'validators_per_shard': 1,
        }
        config['timing'] = {
            'genesis_delay': 30,
            'nodes_start_time': 60,
            'seednode_start_time': 5,
        }

        return config


def merge_configs(leftcfg: ConfigurationType, rightcfg: ConfigurationType) -> ConfigurationType:
    result = dict()
    result.update(leftcfg)

    for key, subcfg in result.items():
        try:
            subcfg.update(rightcfg[key])
        except KeyError:
            pass

    for key in rightcfg:
        if key not in result:
            result[key] = rightcfg[key]

    return result
