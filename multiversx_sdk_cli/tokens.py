from typing import Optional

from multiversx_sdk import (
    GasLimitEstimator,
    TokenManagementTransactionsFactory,
    Transaction,
    TransactionsFactoryConfig,
)

from multiversx_sdk_cli.base_transactions_controller import BaseTransactionsController
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.interfaces import IAccount


class TokenWrapper(BaseTransactionsController):
    def __init__(
        self,
        config: TransactionsFactoryConfig,
        gas_limit_estimator: Optional[GasLimitEstimator] = None,
    ) -> None:
        self.factory = TokenManagementTransactionsFactory(config=config, gas_limit_estimator=gas_limit_estimator)

    def create_transaction_for_issuing_fungible_token(
        self,
        sender: IAccount,
        nonce: int,
        token_name: str,
        token_ticker: str,
        initial_supply: int,
        num_decimals: int,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_issuing_fungible(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            initial_supply=initial_supply,
            num_decimals=num_decimals,
            can_freeze=can_freeze,
            can_wipe=can_wipe,
            can_pause=can_pause,
            can_change_owner=can_change_owner,
            can_upgrade=can_upgrade,
            can_add_special_roles=can_add_special_roles,
        )

        self._set_transaction_fields(
            transaction=tx,
            nonce=nonce,
            version=version,
            options=options,
            gas_price=gas_price,
            guardian_and_relayer_data=guardian_and_relayer_data,
        )

        self.add_extra_gas_limit_if_required(tx)
        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return tx

    def create_transaction_for_issuing_semi_fungible_token(
        self,
        sender: IAccount,
        nonce: int,
        token_name: str,
        token_ticker: str,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_transfer_nft_create_role: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_issuing_semi_fungible(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            can_freeze=can_freeze,
            can_wipe=can_wipe,
            can_pause=can_pause,
            can_transfer_nft_create_role=can_transfer_nft_create_role,
            can_change_owner=can_change_owner,
            can_upgrade=can_upgrade,
            can_add_special_roles=can_add_special_roles,
        )

        self._set_transaction_fields(
            transaction=tx,
            nonce=nonce,
            version=version,
            options=options,
            gas_price=gas_price,
            guardian_and_relayer_data=guardian_and_relayer_data,
        )

        self.add_extra_gas_limit_if_required(tx)
        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return tx

    def create_transaction_for_issuing_non_fungible_token(
        self,
        sender: IAccount,
        nonce: int,
        token_name: str,
        token_ticker: str,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_transfer_nft_create_role: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_issuing_non_fungible(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            can_freeze=can_freeze,
            can_wipe=can_wipe,
            can_pause=can_pause,
            can_transfer_nft_create_role=can_transfer_nft_create_role,
            can_change_owner=can_change_owner,
            can_upgrade=can_upgrade,
            can_add_special_roles=can_add_special_roles,
        )

        self._set_transaction_fields(
            transaction=tx,
            nonce=nonce,
            version=version,
            options=options,
            gas_price=gas_price,
            guardian_and_relayer_data=guardian_and_relayer_data,
        )

        self.add_extra_gas_limit_if_required(tx)
        if gas_limit:
            tx.gas_limit = gas_limit

        self.sign_transaction(
            transaction=tx,
            sender=sender,
            guardian=guardian_and_relayer_data.guardian,
            relayer=guardian_and_relayer_data.relayer,
            guardian_service_url=guardian_and_relayer_data.guardian_service_url,
            guardian_2fa_code=guardian_and_relayer_data.guardian_2fa_code,
        )

        return tx
