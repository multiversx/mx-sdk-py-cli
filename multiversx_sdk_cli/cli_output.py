import json
import logging
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Union

from multiversx_sdk import Transaction, TransactionOnNetwork

from multiversx_sdk_cli import utils
from multiversx_sdk_cli.interfaces import IAddress
from multiversx_sdk_cli.utils import ISerializable

logger = logging.getLogger("cli.output")


class CLIOutputBuilder:
    def __init__(self) -> None:
        self.emitted_transaction_hash: Optional[str] = None
        self.emitted_transaction: Union[Transaction, None] = None
        self.emitted_transaction_omitted_fields: List[str] = []
        self.contract_address: Union[IAddress, None] = None
        self.transaction_on_network: Union[TransactionOnNetwork, None] = None
        self.transaction_on_network_omitted_fields: List[str] = []
        self.simulation_results: Union[ISerializable, None] = None

    def set_emitted_transaction_hash(self, hash: str):
        self.emitted_transaction_hash = hash
        return self

    def set_emitted_transaction(self, emitted_transaction: Transaction, omitted_fields: List[str] = []):
        self.emitted_transaction = emitted_transaction
        self.emitted_transaction_omitted_fields = omitted_fields
        return self

    def set_contract_address(self, contract_address: IAddress):
        self.contract_address = contract_address
        return self

    def set_awaited_transaction(self, awaited_transaction: TransactionOnNetwork, omitted_fields: List[str] = []):
        return self.set_transaction_on_network(awaited_transaction, omitted_fields)

    def set_transaction_on_network(
        self,
        transaction_on_network: TransactionOnNetwork,
        omitted_fields: List[str] = [],
    ):
        self.transaction_on_network = transaction_on_network
        self.transaction_on_network_omitted_fields = omitted_fields
        return self

    def set_simulation_results(self, simulation_results: ISerializable):
        self.simulation_results = simulation_results
        return self

    def build(self) -> Dict[str, Any]:
        output: Dict[str, Any] = OrderedDict()

        if self.emitted_transaction:
            emitted_transaction_dict = self.emitted_transaction.to_dictionary()
            emitted_transaction_hash = self.emitted_transaction_hash or ""
            emitted_transaction_data = self.emitted_transaction.data.decode()
            utils.omit_fields(emitted_transaction_dict, self.emitted_transaction_omitted_fields)

            output["emittedTransaction"] = emitted_transaction_dict
            output["emittedTransactionData"] = emitted_transaction_data
            output["emittedTransactionHash"] = emitted_transaction_hash

        if self.contract_address:
            contract_address = self.contract_address.to_bech32()
            output["contractAddress"] = contract_address

        if self.transaction_on_network:
            transaction_on_network_dict = self.transaction_on_network.raw
            utils.omit_fields(transaction_on_network_dict, self.transaction_on_network_omitted_fields)
            output["transactionOnNetwork"] = transaction_on_network_dict

        if self.simulation_results:
            output["simulation"] = self.simulation_results

        return output

    @classmethod
    def describe(
        cls,
        with_emitted: bool = True,
        with_contract: bool = False,
        with_transaction_on_network: bool = False,
        with_simulation: bool = False,
    ) -> str:
        output: Dict[str, Any] = OrderedDict()

        if with_emitted:
            output["emittedTransaction"] = {
                "nonce": 42,
                "sender": "alice",
                "receiver": "bob",
                "...": "...",
            }
            output["emittedTransactionData"] = "the transaction data, not encoded"
            output["emittedTransactionHash"] = "the transaction hash"

        if with_contract:
            output["contractAddress"] = "the address of the contract"

        if with_transaction_on_network:
            output["transactionOnNetwork"] = {
                "nonce": 42,
                "sender": "alice",
                "receiver": "bob",
                "...": "...",
            }

        if with_simulation:
            output["simulation"] = {"execution": {"...": "..."}, "cost": {"...": "..."}}

        description = json.dumps(output, indent=4)
        description_wrapped = f"""

Output example:
===============
{description}
"""
        return description_wrapped
