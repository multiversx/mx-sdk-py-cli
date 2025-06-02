import logging
from pathlib import Path
from typing import Any, Optional, Protocol, Union

from multiversx_sdk import (
    Address,
    AwaitingOptions,
    SmartContractController,
    SmartContractQuery,
    SmartContractQueryResponse,
    SmartContractTransactionsFactory,
    TokenTransfer,
    Transaction,
    TransactionOnNetwork,
    TransactionsFactoryConfig,
)
from multiversx_sdk.abi import Abi

from multiversx_sdk_cli import errors
from multiversx_sdk_cli.base_transactions_controller import BaseTransactionsController
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.interfaces import IAccount

logger = logging.getLogger("contracts")


# fmt: off
class INetworkProvider(Protocol):
    def query_contract(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        ...

    def await_transaction_completed(
        self, transaction_hash: Union[bytes, str], options: Optional[AwaitingOptions] = None
    ) -> TransactionOnNetwork:
        ...
# fmt: on


class SmartContract(BaseTransactionsController):
    def __init__(self, config: TransactionsFactoryConfig, abi: Optional[Abi] = None):
        self._abi = abi
        self._config = config
        self._factory = SmartContractTransactionsFactory(config, abi)

    def prepare_deploy_transaction(
        self,
        owner: IAccount,
        bytecode: Path,
        arguments: Union[list[Any], None],
        should_prepare_args: bool,
        upgradeable: bool,
        readable: bool,
        payable: bool,
        payable_by_sc: bool,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        args = arguments if arguments else []
        if should_prepare_args:
            args = self._convert_args_to_typed_values(args)

        tx = self._factory.create_transaction_for_deploy(
            sender=owner.address,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=args,
            native_transfer_amount=value,
            is_upgradeable=upgradeable,
            is_readable=readable,
            is_payable=payable,
            is_payable_by_sc=payable_by_sc,
        )
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.gas_price = gas_price
        tx.guardian = guardian_and_relayer_data.guardian_address
        tx.relayer = guardian_and_relayer_data.relayer_address

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return tx

    def prepare_execute_transaction(
        self,
        caller: IAccount,
        contract: Address,
        function: str,
        arguments: Union[list[Any], None],
        should_prepare_args: bool,
        gas_limit: int,
        gas_price: int,
        value: int,
        token_transfers: Union[list[TokenTransfer], None],
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        args = arguments if arguments else []
        if should_prepare_args:
            args = self._convert_args_to_typed_values(args)

        tx = self._factory.create_transaction_for_execute(
            sender=caller.address,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            native_transfer_amount=value,
            token_transfers=token_transfers or [],
        )
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.gas_price = gas_price
        tx.guardian = guardian_and_relayer_data.guardian_address
        tx.relayer = guardian_and_relayer_data.relayer_address

        self.sign_transaction(
            transaction=tx,
            sender=caller,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return tx

    def prepare_upgrade_transaction(
        self,
        owner: IAccount,
        contract: Address,
        bytecode: Path,
        arguments: Union[list[str], None],
        should_prepare_args: bool,
        upgradeable: bool,
        readable: bool,
        payable: bool,
        payable_by_sc: bool,
        gas_limit: int,
        gas_price: int,
        value: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        args = arguments if arguments else []
        if should_prepare_args:
            args = self._convert_args_to_typed_values(args)

        tx = self._factory.create_transaction_for_upgrade(
            sender=owner.address,
            contract=contract,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=args,
            native_transfer_amount=value,
            is_upgradeable=upgradeable,
            is_readable=readable,
            is_payable=payable,
            is_payable_by_sc=payable_by_sc,
        )
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.gas_price = gas_price
        tx.guardian = guardian_and_relayer_data.guardian_address
        tx.relayer = guardian_and_relayer_data.relayer_address

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return tx

    def query_contract(
        self,
        contract_address: Address,
        proxy: INetworkProvider,
        function: str,
        arguments: Optional[list[Any]],
        should_prepare_args: bool,
    ) -> list[Any]:
        args = arguments if arguments else []
        if should_prepare_args:
            args = self._convert_args_to_typed_values(args)

        sc_query_controller = SmartContractController(self._config.chain_id, proxy, self._abi)

        try:
            response = sc_query_controller.query(contract=contract_address, function=function, arguments=args)
        except Exception as e:
            raise errors.QueryContractError("Couldn't query contract: ", e)

        return response
