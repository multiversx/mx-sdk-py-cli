from typing import Optional

from multiversx_sdk import (
    Address,
    GasLimitEstimator,
    TokenManagementTransactionsFactory,
    TokenType,
    Transaction,
    TransactionsFactoryConfig,
)

from multiversx_sdk_cli.base_transactions_controller import BaseTransactionsController
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.interfaces import IAccount


class TokensManagementWrapper(BaseTransactionsController):
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

    def create_transaction_for_registering_meta_esdt(
        self,
        sender: IAccount,
        nonce: int,
        token_name: str,
        token_ticker: str,
        decimals: int,
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
        tx = self.factory.create_transaction_for_registering_meta_esdt(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            num_decimals=decimals,
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

    def create_transaction_for_registering_and_set_all_roles(
        self,
        sender: IAccount,
        nonce: int,
        token_name: str,
        token_ticker: str,
        decimals: int,
        token_type: TokenType,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_registering_and_setting_roles(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            num_decimals=decimals,
            token_type=token_type,
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

    def create_transaction_for_setting_burn_role_globally(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_setting_burn_role_globally(
            sender=sender.address,
            token_identifier=token_identifier,
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

    def create_transaction_for_unsetting_burn_role_globally(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_unsetting_burn_role_globally(
            sender=sender.address,
            token_identifier=token_identifier,
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

    def create_transaction_for_setting_special_role_on_fungible(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        add_role_local_mint: bool,
        add_role_local_burn: bool,
        add_role_esdt_transfer_role: bool,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_setting_special_role_on_fungible_token(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user,
            add_role_local_mint=add_role_local_mint,
            add_role_local_burn=add_role_local_burn,
            add_role_esdt_transfer_role=add_role_esdt_transfer_role,
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

    def create_transaction_for_unsetting_special_role_on_fungible(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        remove_role_local_mint: bool,
        remove_role_local_burn: bool,
        remove_role_esdt_transfer_role: bool,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_unsetting_special_role_on_fungible_token(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user,
            remove_role_local_mint=remove_role_local_mint,
            remove_role_local_burn=remove_role_local_burn,
            remove_role_esdt_transfer_role=remove_role_esdt_transfer_role,
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

    def create_transaction_for_setting_special_role_on_semi_fungible(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        add_role_nft_create: bool,
        add_role_nft_burn: bool,
        add_role_nft_add_quantity: bool,
        add_role_esdt_transfer_role: bool,
        add_role_nft_update: bool,
        add_role_esdt_modify_royalties: bool,
        add_role_esdt_set_new_uri: bool,
        add_role_esdt_modify_creator: bool,
        add_role_nft_recreate: bool,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_setting_special_role_on_semi_fungible_token(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user,
            add_role_nft_create=add_role_nft_create,
            add_role_nft_burn=add_role_nft_burn,
            add_role_nft_add_quantity=add_role_nft_add_quantity,
            add_role_esdt_transfer_role=add_role_esdt_transfer_role,
            add_role_nft_update=add_role_nft_update,
            add_role_esdt_modify_royalties=add_role_esdt_modify_royalties,
            add_role_esdt_set_new_uri=add_role_esdt_set_new_uri,
            add_role_esdt_modify_creator=add_role_esdt_modify_creator,
            add_role_nft_recreate=add_role_nft_recreate,
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

    def create_transaction_for_unsetting_special_role_on_semi_fungible(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        remove_role_nft_burn: bool,
        remove_role_nft_add_quantity: bool,
        remove_role_esdt_transfer_role: bool,
        remove_role_nft_update: bool,
        remove_role_esdt_modify_royalties: bool,
        remove_role_esdt_set_new_uri: bool,
        remove_role_esdt_modify_creator: bool,
        remove_role_nft_recreate: bool,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_unsetting_special_role_on_semi_fungible_token(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user,
            remove_role_nft_burn=remove_role_nft_burn,
            remove_role_nft_add_quantity=remove_role_nft_add_quantity,
            remove_role_esdt_transfer_role=remove_role_esdt_transfer_role,
            remove_role_nft_update=remove_role_nft_update,
            remove_role_esdt_modify_royalties=remove_role_esdt_modify_royalties,
            remove_role_esdt_set_new_uri=remove_role_esdt_set_new_uri,
            remove_role_esdt_modify_creator=remove_role_esdt_modify_creator,
            remove_role_nft_recreate=remove_role_nft_recreate,
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

    def create_transaction_for_setting_special_role_on_meta_esdt(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        add_role_nft_create: bool,
        add_role_nft_burn: bool,
        add_role_nft_add_quantity: bool,
        add_role_esdt_transfer_role: bool,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_setting_special_role_on_meta_esdt(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user,
            add_role_nft_create=add_role_nft_create,
            add_role_nft_burn=add_role_nft_burn,
            add_role_nft_add_quantity=add_role_nft_add_quantity,
            add_role_esdt_transfer_role=add_role_esdt_transfer_role,
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

    def create_transaction_for_unsetting_special_role_on_meta_esdt(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        remove_role_nft_burn: bool,
        remove_role_nft_add_quantity: bool,
        remove_role_esdt_transfer_role: bool,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_unsetting_special_role_on_meta_esdt(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user,
            remove_role_nft_burn=remove_role_nft_burn,
            remove_role_nft_add_quantity=remove_role_nft_add_quantity,
            remove_role_esdt_transfer_role=remove_role_esdt_transfer_role,
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

    def create_transaction_for_setting_special_role_on_non_fungible(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        add_role_nft_create: bool,
        add_role_nft_burn: bool,
        add_role_nft_update_attributes: bool,
        add_role_nft_add_uri: bool,
        add_role_esdt_transfer_role: bool,
        add_role_nft_update: bool,
        add_role_esdt_modify_royalties: bool,
        add_role_esdt_set_new_uri: bool,
        add_role_esdt_modify_creator: bool,
        add_role_nft_recreate: bool,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_setting_special_role_on_non_fungible_token(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user,
            add_role_nft_create=add_role_nft_create,
            add_role_nft_burn=add_role_nft_burn,
            add_role_nft_update_attributes=add_role_nft_update_attributes,
            add_role_nft_add_uri=add_role_nft_add_uri,
            add_role_esdt_transfer_role=add_role_esdt_transfer_role,
            add_role_nft_update=add_role_nft_update,
            add_role_esdt_modify_royalties=add_role_esdt_modify_royalties,
            add_role_esdt_set_new_uri=add_role_esdt_set_new_uri,
            add_role_esdt_modify_creator=add_role_esdt_modify_creator,
            add_role_nft_recreate=add_role_nft_recreate,
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

    def create_transaction_for_unsetting_special_role_on_non_fungible(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        remove_role_nft_burn: bool,
        remove_role_nft_update_attributes: bool,
        remove_role_nft_add_uri: bool,
        remove_role_esdt_transfer_role: bool,
        remove_role_nft_update: bool,
        remove_role_esdt_modify_royalties: bool,
        remove_role_esdt_set_new_uri: bool,
        remove_role_esdt_modify_creator: bool,
        remove_role_nft_recreate: bool,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_unsetting_special_role_on_non_fungible_token(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user,
            remove_role_nft_burn=remove_role_nft_burn,
            remove_role_nft_update_attributes=remove_role_nft_update_attributes,
            remove_role_nft_remove_uri=remove_role_nft_add_uri,
            remove_role_esdt_transfer_role=remove_role_esdt_transfer_role,
            remove_role_nft_update=remove_role_nft_update,
            remove_role_esdt_modify_royalties=remove_role_esdt_modify_royalties,
            remove_role_esdt_set_new_uri=remove_role_esdt_set_new_uri,
            remove_role_esdt_modify_creator=remove_role_esdt_modify_creator,
            remove_role_nft_recreate=remove_role_nft_recreate,
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

    def create_transaction_for_creating_nft(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        initial_quantity: int,
        name: str,
        royalties: int,
        hash: str,
        attributes: bytes,
        uris: list[str],
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_creating_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            initial_quantity=initial_quantity,
            name=name,
            royalties=royalties,
            hash=hash,
            attributes=attributes,
            uris=uris,
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

    def create_transaction_for_pausing(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_pausing(
            sender=sender.address,
            token_identifier=token_identifier,
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

    def create_transaction_for_unpausing(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_unpausing(
            sender=sender.address,
            token_identifier=token_identifier,
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

    def create_transaction_for_freezing(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        user: Address,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_freezing(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user,
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

    def create_transaction_for_unfreezing(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        user: Address,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_unfreezing(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user,
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

    def create_transaction_for_wiping(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        user: Address,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_wiping(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
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

    def create_transaction_for_local_minting(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        supply_to_mint: int,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_local_minting(
            sender=sender.address,
            token_identifier=token_identifier,
            supply_to_mint=supply_to_mint,
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

    def create_transaction_for_local_burning(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        supply_to_burn: int,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_local_burning(
            sender=sender.address,
            token_identifier=token_identifier,
            supply_to_burn=supply_to_burn,
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

    def create_transaction_for_updating_attributes(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        attributes: bytes,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_updating_attributes(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            attributes=attributes,
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

    def create_transaction_for_adding_quantity(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        quantity: int,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_adding_quantity(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            quantity_to_add=quantity,
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

    def create_transaction_for_burning_quantity(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        quantity: int,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_burning_quantity(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            quantity_to_burn=quantity,
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

    def create_transaction_for_modifying_royalties(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        royalties: int,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_modifying_royalties(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            new_royalties=royalties,
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

    def create_transaction_for_setting_new_uris(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        uris: list[str],
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_setting_new_uris(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            new_uris=uris,
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

    def create_transaction_for_modifying_creator(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_modifying_creator(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
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

    def create_transaction_for_updating_metadata(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        new_token_name: str,
        new_royalties: int,
        new_hash: str,
        new_attributes: bytes,
        new_uris: list[str],
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_updating_metadata(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            new_token_name=new_token_name,
            new_royalties=new_royalties,
            new_hash=new_hash,
            new_attributes=new_attributes,
            new_uris=new_uris,
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

    def create_transaction_for_recreating_metadata(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        new_token_name: str,
        new_royalties: int,
        new_hash: str,
        new_attributes: bytes,
        new_uris: list[str],
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_nft_metadata_recreate(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            new_token_name=new_token_name,
            new_royalties=new_royalties,
            new_hash=new_hash,
            new_attributes=new_attributes,
            new_uris=new_uris,
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

    def create_transaction_for_changing_token_to_dynamic(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_changing_token_to_dynamic(
            sender=sender.address,
            token_identifier=token_identifier,
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

    def create_transaction_for_updating_token_id(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_updating_token_id(
            sender=sender.address,
            token_identifier=token_identifier,
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

    def create_transaction_for_registering_dynamic_token(
        self,
        sender: IAccount,
        nonce: int,
        token_name: str,
        token_ticker: str,
        token_type: TokenType,
        denominator: Optional[int],
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_registering_dynamic_token(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            token_type=token_type,
            denominator=denominator,
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

    def create_transaction_for_registering_dynamic_and_setting_roles(
        self,
        sender: IAccount,
        nonce: int,
        token_name: str,
        token_ticker: str,
        token_type: TokenType,
        denominator: Optional[int],
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_registering_dynamic_and_setting_roles(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            token_type=token_type,
            denominator=denominator,
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

    def create_transaction_for_transferring_ownership(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        new_owner: Address,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_transferring_ownership(
            sender=sender.address,
            token_identifier=token_identifier,
            new_owner=new_owner,
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

    def create_transaction_for_freezing_single_nft(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        user: Address,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_freezing_single_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            user=user,
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

    def create_transaction_for_unfreezing_single_nft(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        user: Address,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_unfreezing_single_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            user=user,
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

    def create_transaction_for_changing_sft_to_meta_esdt(
        self,
        sender: IAccount,
        nonce: int,
        collection_identifier: str,
        decimals: int,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_changing_sft_to_meta_esdt(
            sender=sender.address,
            collection=collection_identifier,
            num_decimals=decimals,
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

    def create_transaction_for_transferring_nft_create_role(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        user: Address,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_transferring_nft_create_role(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user,
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

    def create_transaction_for_stopping_nft_creation(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_stopping_nft_creation(
            sender=sender.address,
            token_identifier=token_identifier,
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

    def create_transaction_for_wiping_single_nft(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        user: Address,
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_wiping_single_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            user=user,
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

    def create_transaction_for_adding_uris(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        uris: list[str],
        gas_limit: Optional[int],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transction_for_adding_uris(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            uris=uris,
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
