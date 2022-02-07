from collections import OrderedDict
import json
from typing import Any, Dict, List, Union
import logging
from erdpy import utils

from erdpy.accounts import Address
from erdpy.interfaces import ITransaction
from erdpy.utils import ISerializable

logger = logging.getLogger("cli.output")


class CLIOutputBuilder:
    def __init__(self) -> None:
        self.emitted_transaction: Union[ITransaction, None] = None
        self.emitted_transaction_omitted_fields: List[str] = []
        self.contract_address: Union[Address, None] = None
        self.awaited_transaction: Union[ISerializable, None] = None
        self.awaited_transaction_omitted_fields: List[str] = []
        self.simulation_results: Union[ISerializable, None] = None

    def set_emitted_transaction(self, emitted_transaction: ITransaction, omitted_fields: List[str] = []):
        self.emitted_transaction = emitted_transaction
        self.emitted_transaction_omitted_fields = omitted_fields
        return self

    def set_contract_address(self, contract_address: Address):
        self.contract_address = contract_address
        return self

    def set_awaited_transaction(self, awaited_transaction: ISerializable, omitted_fields: List[str] = []):
        self.awaited_transaction = awaited_transaction
        self.awaited_transaction_omitted_fields = omitted_fields
        return self

    def set_simulation_results(self, simulation_results: ISerializable):
        self.simulation_results = simulation_results
        return self

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

            logger.warn("The fields 'tx', 'data', 'hash' are deprecated and will be removed in a future version. Please rely on 'emittedTransaction', 'emittedTransactionData' and 'emittedTransactionHash' instead.")
            output["tx"] = emitted_transaction_dict
            output["data"] = emitted_transaction_data
            output["hash"] = emitted_transaction_hash

            logger.warn("The field 'emitted_tx' is deprecated and will be removed in a future version. Please rely on 'emittedTransaction' instead.")
            output["emitted_tx"] = {
                "tx": emitted_transaction_dict,
                "hash": emitted_transaction_hash,
                "data": emitted_transaction_data
            }

        if self.contract_address:
            contract_address = self.contract_address.bech32()
            output["contractAddress"] = contract_address

            logger.warn("The field 'emitted_tx.address' is deprecated and will be removed in a future version. Please rely on 'contractAddress' instead.")
            if "emitted_tx" in output:
                output["emitted_tx"]["address"] = contract_address

        if self.awaited_transaction:
            awaited_transaction_dict = self.awaited_transaction.to_dictionary()
            utils.omit_fields(awaited_transaction_dict, self.awaited_transaction_omitted_fields)
            output["awaitedTransaction"] = awaited_transaction_dict

        if self.simulation_results:
            output["simulation"] = self.simulation_results

        return output

    @classmethod
    def describe(cls, with_emitted: bool = True, with_contract: bool = False, with_awaited_transaction: bool = False, with_simulation: bool = False) -> str:
        output: Dict[str, Any] = OrderedDict()

        if with_emitted:
            output["emittedTransaction"] = {"nonce": 42, "sender": "alice", "receiver": "bob", "...": "..."}
            output["emittedTransactionData"] = "the transaction data, not encoded"
            output["emittedTransactionHash"] = "the transaction hash"

            output["tx"] = {"DEPRECATED": "DEPRECATED"}
            output["data"] = "DEPRECATED"
            output["hash"] = "DEPRECATED"

        if with_contract:
            output["emitted_tx"] = {"DEPRECATED": "DEPRECATED"}
            output["contractAddress"] = "the address of the contract (in case of deployments)"

        if with_awaited_transaction:
            output["awaitedTransaction"] = {"nonce": 42, "sender": "alice", "receiver": "bob", "...": "..."}

        if with_simulation:
            output["simulation"] = {
                "execution": {"...": "..."},
                "cost": {"...": "..."}
            }

        description = json.dumps(output, indent=4)
        description_wrapped = f"""

Output example:
===============
{description}
"""
        return description_wrapped
