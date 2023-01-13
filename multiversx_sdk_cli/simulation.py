from collections import OrderedDict
from typing import Any, Dict, Protocol
from multiversx_sdk_cli.interfaces import ISimulateResponse, ITransaction
from multiversx_sdk_cli.utils import ISerializable


class INetworkProvider(Protocol):
    def simulate_transaction(self, transaction: ITransaction) -> ISimulateResponse:
        ...


class Simulation(ISerializable):
    def __init__(self, simulate_response: ISimulateResponse) -> None:
        self.simulation_response = simulate_response

    def to_dictionary(self) -> Dict[str, Any]:
        dictionary: Dict[str, Any] = OrderedDict()
        dictionary["execution"] = self.simulation_response.to_dictionary()

        return dictionary

class Simulator():
    def __init__(self, proxy: INetworkProvider) -> None:
        self.proxy = proxy

    def run(self, transaction: ITransaction) -> Simulation:
        simulation_response = self.proxy.simulate_transaction(transaction)

        return Simulation(simulation_response)
