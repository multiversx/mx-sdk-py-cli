from collections import OrderedDict
from typing import Any, Dict
from erdpy.interfaces import IElrondProxy, ISimulateCostResponse, ISimulateResponse, ITransaction
from erdpy.utils import ISerializable


class Simulation(ISerializable):
    def __init__(self, simulate_response: ISimulateResponse, simulate_cost_response: ISimulateCostResponse) -> None:
        self.simulation_response = simulate_response
        self.cost_simulation_response = simulate_cost_response

    def to_dictionary(self) -> Dict[str, Any]:
        dictionary: Dict[str, Any] = OrderedDict()
        dictionary["execution"] = self.simulation_response.to_dictionary()
        dictionary["cost"] = self.cost_simulation_response.to_dictionary()

        return dictionary

class Simulator():
    def __init__(self, proxy: IElrondProxy) -> None:
        self.proxy = proxy

    def run(self, transaction: ITransaction) -> Simulation:
        dictionary = transaction.to_dictionary()
        simulation_response = self.proxy.simulate_transaction(dictionary)
        cost_simulation_response = self.proxy.simulate_transaction_cost(dictionary)

        return Simulation(simulation_response, cost_simulation_response)

