from typing import Optional

from multiversx_sdk import (
    Address,
    GasLimitEstimator,
    Transaction,
    TransactionsFactoryConfig,
    ValidatorPublicKey,
    ValidatorsSigners,
    ValidatorsTransactionsFactory,
)

from multiversx_sdk_cli.base_transactions_controller import BaseTransactionsController
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.interfaces import IAccount


class ValidatorsController(BaseTransactionsController):
    def __init__(self, chain_id: str, gas_limit_estimator: Optional[GasLimitEstimator] = None) -> None:
        self.factory = ValidatorsTransactionsFactory(
            config=TransactionsFactoryConfig(chain_id),
            gas_limit_estimator=gas_limit_estimator,
        )

    def create_transaction_for_staking(
        self,
        sender: IAccount,
        validators: ValidatorsSigners,
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
        rewards_address: Optional[Address] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_staking(
            sender=sender.address,
            validators_file=validators,
            amount=native_amount,
            rewards_address=rewards_address,
        )
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_topping_up(
        self,
        sender: IAccount,
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_topping_up(
            sender=sender.address,
            amount=native_amount,
        )
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_unstaking(
        self,
        sender: IAccount,
        keys: list[ValidatorPublicKey],
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unstaking(
            sender=sender.address,
            public_keys=keys,
        )
        transaction.value = native_amount
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_unjailing(
        self,
        sender: IAccount,
        keys: list[ValidatorPublicKey],
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unjailing(
            sender=sender.address,
            public_keys=keys,
            amount=native_amount,
        )
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_unbonding(
        self,
        sender: IAccount,
        keys: list[ValidatorPublicKey],
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unbonding(
            sender=sender.address,
            public_keys=keys,
        )
        transaction.value = native_amount
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_changing_rewards_address(
        self,
        sender: IAccount,
        rewards_address: Address,
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_changing_rewards_address(
            sender=sender.address,
            rewards_address=rewards_address,
        )
        transaction.value = native_amount
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_claiming(
        self,
        sender: IAccount,
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_claiming(
            sender=sender.address,
        )
        transaction.value = native_amount
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_unstaking_nodes(
        self,
        sender: IAccount,
        keys: list[ValidatorPublicKey],
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unstaking_nodes(
            sender=sender.address,
            public_keys=keys,
        )
        transaction.value = native_amount
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_unstaking_tokens(
        self,
        sender: IAccount,
        value: int,
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unstaking_tokens(
            sender=sender.address,
            amount=value,
        )
        transaction.value = native_amount
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_unbonding_nodes(
        self,
        sender: IAccount,
        keys: list[ValidatorPublicKey],
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unbonding_nodes(
            sender=sender.address,
            public_keys=keys,
        )
        transaction.value = native_amount
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_unbonding_tokens(
        self,
        sender: IAccount,
        value: int,
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unbonding_tokens(
            sender=sender.address,
            amount=value,
        )
        transaction.value = native_amount
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_cleaning_registered_data(
        self,
        sender: IAccount,
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_cleaning_registered_data(
            sender=sender.address,
        )
        transaction.value = native_amount
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction

    def create_transaction_for_restaking_unstaked_nodes(
        self,
        sender: IAccount,
        keys: list[ValidatorPublicKey],
        native_amount: int,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_restaking_unstaked_nodes(
            sender=sender.address,
            public_keys=keys,
        )
        transaction.value = native_amount
        transaction.gas_price = gas_price
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address

        self.add_extra_gas_limit_if_required(transaction)

        if gas_limit:
            transaction.gas_limit = gas_limit

        self.sign_transaction(
            transaction=transaction,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return transaction
