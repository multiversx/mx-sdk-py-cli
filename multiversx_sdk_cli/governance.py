from typing import Optional, Union

from multiversx_sdk import (
    Address,
    GasLimitEstimator,
    GovernanceTransactionsFactory,
    Transaction,
    TransactionsFactoryConfig,
    VoteType,
)

from multiversx_sdk_cli.base_transactions_controller import BaseTransactionsController
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.interfaces import IAccount


class GovernanceWrapper(BaseTransactionsController):
    def __init__(
        self,
        config: TransactionsFactoryConfig,
        gas_limit_estimator: Optional[GasLimitEstimator] = None,
    ) -> None:
        self.factory = GovernanceTransactionsFactory(config=config, gas_limit_estimator=gas_limit_estimator)

    def create_transaction_for_new_proposal(
        self,
        sender: IAccount,
        nonce: int,
        commit_hash: str,
        start_vote_epoch: int,
        end_vote_epoch: int,
        native_token_amount: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_new_proposal(
            sender=sender.address,
            commit_hash=commit_hash,
            start_vote_epoch=start_vote_epoch,
            end_vote_epoch=end_vote_epoch,
            native_token_amount=native_token_amount,
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

    def create_transaction_for_voting(
        self,
        sender: IAccount,
        nonce: int,
        proposal_nonce: int,
        vote: str,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        vote_value = self._vote_type_from_string(vote)

        tx = self.factory.create_transaction_for_voting(
            sender=sender.address, proposal_nonce=proposal_nonce, vote=vote_value
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

    def create_transaction_for_closing_proposal(
        self,
        sender: IAccount,
        nonce: int,
        proposal_nonce: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_closing_proposal(sender=sender.address, proposal_nonce=proposal_nonce)
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

    def create_transaction_for_clearing_ended_proposals(
        self,
        sender: IAccount,
        nonce: int,
        proposers: list[Address],
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_clearing_ended_proposals(sender=sender.address, proposers=proposers)
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

    def create_transaction_for_claiming_accumulated_fees(
        self,
        sender: IAccount,
        nonce: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_claiming_accumulated_fees(sender=sender.address)
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

    def create_transaction_for_changing_config(
        self,
        sender: IAccount,
        nonce: int,
        proposal_fee: int,
        lost_proposal_fee: int,
        min_quorum: int,
        min_veto_threshold: int,
        min_pass_threshold: int,
        gas_limit: Union[int, None],
        gas_price: int,
        version: int,
        options: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ) -> Transaction:
        tx = self.factory.create_transaction_for_changing_config(
            sender=sender.address,
            proposal_fee=proposal_fee,
            lost_proposal_fee=lost_proposal_fee,
            min_quorum=min_quorum,
            min_veto_threshold=min_veto_threshold,
            min_pass_threshold=min_pass_threshold,
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

    def _vote_type_from_string(self, value: str) -> VoteType:
        for vote in VoteType:
            if vote.value == value:
                return vote
        raise ValueError(f"Unknown vote type: {value}")
