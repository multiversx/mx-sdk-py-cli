from collections import OrderedDict
from typing import Any, Dict, Protocol

from multiversx_sdk_cli.utils import ISerializable
from multiversx_sdk import Transaction, TransactionOnNetwork


class INetworkProvider(Protocol):
    def simulate_transaction(self, transaction: Transaction) -> TransactionOnNetwork:
        ...


class Simulation(ISerializable):
    def __init__(self, simulate_response: TransactionOnNetwork) -> None:
        self.simulation_response = simulate_response

    def to_dictionary(self) -> Dict[str, Any]:
        dictionary: Dict[str, Any] = OrderedDict()
        dictionary["execution"] = self.simulation_response.raw

        return dictionary


class Simulator():
    def __init__(self, proxy: INetworkProvider) -> None:
        self.proxy = proxy

    def run(self, transaction: Transaction) -> Simulation:
        simulation_response = self.proxy.simulate_transaction(transaction)

        return Simulation(simulation_response)
