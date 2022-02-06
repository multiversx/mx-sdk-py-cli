from collections import OrderedDict
from typing import Any, Dict, List, Union
from erdpy import utils

from erdpy.accounts import Address
from erdpy.interfaces import ITransaction
from erdpy.utils import ISerializable


class CLIOutputBuilder:
    def __init__(self) -> None:
        self.emitted_transaction: Union[ITransaction, None] = None
        self.emitted_transaction_omitted_fields: List[str] = []
        self.contract_address: Union[Address, None] = None
        self.transaction_on_network: Union[ISerializable, None] = None
        self.transaction_on_network_omitted_fields: List[str] = []
        self.simulation_results: Union[ISerializable, None] = None

    def set_emitted_transaction(self, emitted_transaction: ITransaction, omitted_fields: List[str] = []):
        self.emitted_transaction = emitted_transaction
        self.emitted_transaction_omitted_fields = omitted_fields
        return self

    def set_contract_address(self, contract_address: Address):
        self.contract_address = contract_address
        return self

    def set_transaction_on_network(self, transaction_on_network: ISerializable, omitted_fields: List[str] = []):
        self.transaction_on_network = transaction_on_network
        self.transaction_on_network_omitted_fields = omitted_fields
        return self

    def set_simulation_results(self, simulation_results: ISerializable):
        self.simulation_results = simulation_results
        return self

    # TODO: Remove redundant fields in future versions of erdpy.
    # Currently, the following deprecated fields are kept for backwards compatibility:
    # tx, hash, data, emitted_tx, emitted_tx.*
    def build(self) -> Dict[str, Any]:
        output: Dict[str, Any] = OrderedDict()

        if self.emitted_transaction:
            emitted_transaction_dict = self.emitted_transaction.to_dictionary()
            emitted_transaction_hash = self.emitted_transaction.get_hash() or ""
            emitted_transaction_data = self.emitted_transaction.get_data() or ""
            utils.omit_fields(emitted_transaction_dict, self.emitted_transaction_omitted_fields)

            output["emittedTransaction"] = emitted_transaction_dict
            output["emittedTransactionData"] = emitted_transaction_data
            output["emittedTransactionHash"] = emitted_transaction_hash

            # For backwards compatibility (some scripts might rely on these fields):
            output["tx"] = emitted_transaction_dict
            output["data"] = emitted_transaction_data
            output["hash"] = emitted_transaction_hash

            # For backwards compatibility (a lot of interaction scripts rely on "emitted_tx"):
            output["emitted_tx"] = {
                "tx": emitted_transaction_dict,
                "hash": emitted_transaction_hash,
                "data": emitted_transaction_data
            }

        if self.contract_address:
            contract_address = self.contract_address.bech32()

            output["contractAddress"] = contract_address

            # For backwards compatibility (a lot of interaction scripts rely on "emitted_tx"):
            if "emitted_tx" in output:
                output["emitted_tx"]["address"] = contract_address

        if self.transaction_on_network:
            transaction_on_network_dict = self.transaction_on_network.to_dictionary()
            utils.omit_fields(transaction_on_network_dict, self.transaction_on_network_omitted_fields)

            output["transactionOnNetwork"] = transaction_on_network_dict

        if self.simulation_results:
            output["simulation"] = self.simulation_results

        return output
