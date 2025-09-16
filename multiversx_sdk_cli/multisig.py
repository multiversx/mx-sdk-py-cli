import logging
from pathlib import Path
from typing import Any, Optional, Union

from multiversx_sdk import (
    Address,
    GasLimitEstimator,
    MultisigTransactionsFactory,
    TokenTransfer,
    Transaction,
    TransactionsFactoryConfig,
)
from multiversx_sdk.abi import Abi

from multiversx_sdk_cli.base_transactions_controller import BaseTransactionsController
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.interfaces import IAccount

logger = logging.getLogger("multisig")


class MultisigWrapper(BaseTransactionsController):
    def __init__(
        self,
        config: TransactionsFactoryConfig,
        abi: Abi,
        gas_limit_estimator: Optional[GasLimitEstimator] = None,
    ):
        self._factory = MultisigTransactionsFactory(config=config, abi=abi, gas_limit_estimator=gas_limit_estimator)

    def prepare_deploy_transaction(
        self,
        owner: IAccount,
        nonce: int,
        bytecode: Path,
        quorum: int,
        board_members: list[Address],
        upgradeable: bool,
        readable: bool,
        payable: bool,
        payable_by_sc: bool,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_deploy(
            sender=owner.address,
            bytecode=bytecode,
            quorum=quorum,
            board=board_members,
            gas_limit=gas_limit,
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

    def prepare_deposit_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
        native_amount: Optional[int] = None,
        token_transfers: Optional[list[TokenTransfer]] = None,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_deposit(
            sender=owner.address,
            contract=contract,
            gas_limit=gas_limit,
            native_token_amount=native_amount,
            token_transfers=token_transfers,
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

    def prepare_discard_action_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_discard_action(
            sender=owner.address,
            contract=contract,
            action_id=action_id,
            gas_limit=gas_limit,
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

    def prepare_discard_batch_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        action_ids: list[int],
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_discard_batch(
            sender=owner.address,
            contract=contract,
            action_ids=action_ids,
            gas_limit=gas_limit,
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

    def prepare_add_board_member_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        board_member: Address,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_propose_add_board_member(
            sender=owner.address,
            contract=contract,
            board_member=board_member,
            gas_limit=gas_limit,
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

    def prepare_add_proposer_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        proposer: Address,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_propose_add_proposer(
            sender=owner.address,
            contract=contract,
            proposer=proposer,
            gas_limit=gas_limit,
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

    def prepare_remove_user_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        user: Address,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_propose_remove_user(
            sender=owner.address,
            contract=contract,
            user=user,
            gas_limit=gas_limit,
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

    def prepare_change_quorum_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        quorum: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_propose_change_quorum(
            sender=owner.address,
            contract=contract,
            quorum=quorum,
            gas_limit=gas_limit,
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

    def prepare_transfer_execute_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        receiver: Address,
        native_token_amount: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        should_prepare_args_for_factory: bool,
        guardian_and_relayer_data: GuardianRelayerData,
        opt_gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
        function: Optional[str] = None,
        arguments: Optional[list[Any]] = None,
    ) -> Transaction:
        args = arguments if arguments else []
        if should_prepare_args_for_factory:
            args = self._convert_args_to_typed_values(args)

        tx = self._factory.create_transaction_for_propose_transfer_execute(
            sender=owner.address,
            contract=contract,
            receiver=receiver,
            native_token_amount=native_token_amount,
            gas_limit=gas_limit,
            opt_gas_limit=opt_gas_limit,
            abi=abi,
            function=function,
            arguments=args,
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

    def prepare_transfer_execute_esdt_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        receiver: Address,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        should_prepare_args_for_factory: bool,
        guardian_and_relayer_data: GuardianRelayerData,
        token_transfers: list[TokenTransfer],
        opt_gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
        function: Optional[str] = None,
        arguments: Optional[list[Any]] = None,
    ) -> Transaction:
        args = arguments if arguments else []
        if should_prepare_args_for_factory:
            args = self._convert_args_to_typed_values(args)

        tx = self._factory.create_transaction_for_propose_transfer_esdt_execute(
            sender=owner.address,
            contract=contract,
            receiver=receiver,
            token_transfers=token_transfers,
            gas_limit=gas_limit,
            opt_gas_limit=opt_gas_limit,
            abi=abi,
            function=function,
            arguments=args,
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

    def prepare_async_call_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        receiver: Address,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        should_prepare_args_for_factory: bool,
        guardian_and_relayer_data: GuardianRelayerData,
        native_token_amount: int = 0,
        token_transfers: Optional[list[TokenTransfer]] = None,
        opt_gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
        function: Optional[str] = None,
        arguments: Optional[list[Any]] = None,
    ) -> Transaction:
        args = arguments if arguments else []
        if should_prepare_args_for_factory:
            args = self._convert_args_to_typed_values(args)

        tx = self._factory.create_transaction_for_propose_async_call(
            sender=owner.address,
            contract=contract,
            receiver=receiver,
            gas_limit=gas_limit,
            native_token_amount=native_token_amount,
            token_transfers=token_transfers,
            opt_gas_limit=opt_gas_limit,
            abi=abi,
            function=function,
            arguments=args,
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

    def prepare_contract_deploy_from_source_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        contract_to_copy: Address,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        upgradeable: bool,
        readable: bool,
        payable: bool,
        payable_by_sc: bool,
        should_prepare_args_for_factory: bool,
        guardian_and_relayer_data: GuardianRelayerData,
        native_token_amount: int = 0,
        abi: Optional[Abi] = None,
        arguments: Optional[list[Any]] = None,
    ) -> Transaction:
        args = arguments if arguments else []
        if should_prepare_args_for_factory:
            args = self._convert_args_to_typed_values(args)

        tx = self._factory.create_transaction_for_propose_contract_deploy_from_source(
            sender=owner.address,
            contract=contract,
            gas_limit=gas_limit,
            contract_to_copy=contract_to_copy,
            is_upgradeable=upgradeable,
            is_readable=readable,
            is_payable=payable,
            is_payable_by_sc=payable_by_sc,
            native_token_amount=native_token_amount,
            abi=abi,
            arguments=args,
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

    def prepare_contract_upgrade_from_source_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        contract_to_upgrade: Address,
        contract_to_copy: Address,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        upgradeable: bool,
        readable: bool,
        payable: bool,
        payable_by_sc: bool,
        should_prepare_args_for_factory: bool,
        guardian_and_relayer_data: GuardianRelayerData,
        native_token_amount: int = 0,
        abi: Optional[Abi] = None,
        arguments: Optional[list[Any]] = None,
    ) -> Transaction:
        args = arguments if arguments else []
        if should_prepare_args_for_factory:
            args = self._convert_args_to_typed_values(args)

        tx = self._factory.create_transaction_for_propose_contract_upgrade_from_source(
            sender=owner.address,
            contract=contract,
            contract_to_upgrade=contract_to_upgrade,
            contract_to_copy=contract_to_copy,
            gas_limit=gas_limit,
            is_upgradeable=upgradeable,
            is_readable=readable,
            is_payable=payable,
            is_payable_by_sc=payable_by_sc,
            native_token_amount=native_token_amount,
            abi=abi,
            arguments=args,
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

    def prepare_sign_action_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_sign_action(
            sender=owner.address,
            contract=contract,
            action_id=action_id,
            gas_limit=gas_limit,
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

    def prepare_sign_batch_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        batch_id: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_sign_batch(
            sender=owner.address,
            contract=contract,
            batch_id=batch_id,
            gas_limit=gas_limit,
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

    def prepare_sign_and_perform_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_sign_and_perform(
            sender=owner.address,
            contract=contract,
            action_id=action_id,
            gas_limit=gas_limit,
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

    def prepare_sign_batch_and_perform_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        batch_id: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_sign_batch_and_perform(
            sender=owner.address,
            contract=contract,
            batch_id=batch_id,
            gas_limit=gas_limit,
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

    def prepare_unsign_action_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_unsign_action(
            sender=owner.address,
            contract=contract,
            action_id=action_id,
            gas_limit=gas_limit,
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

    def prepare_unsign_batch_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        batch_id: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_unsign_batch(
            sender=owner.address,
            contract=contract,
            batch_id=batch_id,
            gas_limit=gas_limit,
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

    def prepare_unsign_for_outdated_board_members_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        outdated_board_members: list[int],
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_unsign_for_outdated_board_members(
            sender=owner.address,
            contract=contract,
            action_id=action_id,
            outdated_board_members=outdated_board_members,
            gas_limit=gas_limit,
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

    def prepare_perform_action_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_perform_action(
            sender=owner.address,
            contract=contract,
            action_id=action_id,
            gas_limit=gas_limit,
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

    def prepare_perform_batch_transaction(
        self,
        owner: IAccount,
        nonce: int,
        contract: Address,
        batch_id: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self._factory.create_transaction_for_perform_batch(
            sender=owner.address,
            contract=contract,
            batch_id=batch_id,
            gas_limit=gas_limit,
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
