from typing import Any, Dict

from multiversx_sdk_cli.localnet.config_part import ConfigPart


class Networking(ConfigPart):
    def __init__(self,
                 host: str,
                 port_seednode: int,
                 p2p_id_seednode: str,
                 port_proxy: int,
                 port_first_observer: int,
                 port_first_observer_rest_api: int,
                 port_first_validator: int,
                 port_first_validator_rest_api: int):
        self.host: str = host
        self.port_seednode: int = port_seednode
        self.p2p_id_seednode: str = p2p_id_seednode
        self.port_proxy: int = port_proxy
        self.port_first_observer: int = port_first_observer
        self.port_first_observer_rest_api: int = port_first_observer_rest_api
        self.port_first_validator: int = port_first_validator
        self.port_first_validator_rest_api: int = port_first_validator_rest_api

    def get_name(self) -> str:
        return "networking"

    def _do_override(self, other: Dict[str, Any]):
        self.host = other.get("host", self.host)
        self.port_seednode = other.get("port_seednode", self.port_seednode)
        self.p2p_id_seednode = other.get("p2p_id_seednode", self.p2p_id_seednode)
        self.port_proxy = other.get("port_proxy", self.port_proxy)
        self.port_first_observer = other.get("port_first_observer", self.port_first_observer)
        self.port_first_observer_rest_api = other.get("port_first_observer_rest_api", self.port_first_observer_rest_api)
        self.port_first_validator = other.get("port_first_validator", self.port_first_validator)
        self.port_first_validator_rest_api = other.get("port_first_validator_rest_api", self.port_first_validator_rest_api)

    def get_proxy_url(self) -> str:
        return f"http://{self.host}:{self.port_proxy}"
