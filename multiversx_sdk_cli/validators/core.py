import logging
from pathlib import Path
from typing import Any, Optional, Union

from multiversx_sdk import Address, Transaction
from multiversx_sdk.abi import (
    AddressValue,
    BigUIntValue,
    BytesValue,
    Serializer,
    U32Value,
)

from multiversx_sdk_cli import utils
from multiversx_sdk_cli.config import MetaChainSystemSCsCost, get_address_hrp
from multiversx_sdk_cli.constants import GAS_PER_DATA_BYTE, MIN_GAS_LIMIT
from multiversx_sdk_cli.interfaces import IAccount
from multiversx_sdk_cli.transactions import TransactionsController
from multiversx_sdk_cli.validators.validators_file import ValidatorsFile

logger = logging.getLogger("validators")

VALIDATORS_SMART_CONTRACT_ADDRESS_HEX = "000000000000000000010000000000000000000000000000000000000001ffff"


class ValidatorsController:
    def __init__(self, chain_id: str) -> None:
        self.transactions_controller = TransactionsController(chain_id)
        self.serializer = Serializer()

    def create_transaction_for_staking(
        self,
        sender: IAccount,
        validators_file: Path,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        rewards_address: Optional[Address] = None,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        validators = ValidatorsFile(validators_file)
        data = self.prepare_transaction_data_for_stake(
            node_operator=sender.address,
            validators_file=validators,
            rewards_address=rewards_address,
        )

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.STAKE, validators.get_num_of_nodes())

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def prepare_transaction_data_for_stake(
        self,
        node_operator: Address,
        validators_file: ValidatorsFile,
        rewards_address: Union[Address, None],
    ) -> str:
        num_of_nodes = validators_file.get_num_of_nodes()

        call_arguments: list[Any] = []
        call_arguments.append(U32Value(num_of_nodes))

        validator_signers = validators_file.load_signers()

        for validator in validator_signers:
            signed_message = validator.sign(node_operator.get_public_key())

            call_arguments.append(BytesValue(validator.secret_key.generate_public_key().buffer))
            call_arguments.append(BytesValue(signed_message))

        if rewards_address:
            call_arguments.append(AddressValue.new_from_address(rewards_address))

        data = "stake@" + self.serializer.serialize(call_arguments)
        return data

    def create_transaction_for_topping_up(
        self,
        sender: IAccount,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        data = "stake"
        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.STAKE, 1)

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def create_transaction_for_unstaking(
        self,
        sender: IAccount,
        keys: str,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        parsed_keys, num_keys = utils.parse_keys(keys)
        data = f"unStake{parsed_keys}"

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.UNSTAKE, num_keys)

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def create_transaction_for_unjailing(
        self,
        sender: IAccount,
        keys: str,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        parsed_keys, num_keys = utils.parse_keys(keys)
        data = f"unJail{parsed_keys}"

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.UNJAIL, num_keys)

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def create_transaction_for_unbonding(
        self,
        sender: IAccount,
        keys: str,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        parsed_keys, num_keys = utils.parse_keys(keys)
        data = f"unBond{parsed_keys}"

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.UNBOND, num_keys)

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def create_transaction_for_changing_rewards_address(
        self,
        sender: IAccount,
        rewards_address: Address,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        data = f"changeRewardAddress@{rewards_address.to_hex()}"

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.CHANGE_REWARD_ADDRESS)

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def create_transaction_for_claiming(
        self,
        sender: IAccount,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        data = "claim"

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.CLAIM)

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def create_transaction_for_unstaking_nodes(
        self,
        sender: IAccount,
        keys: str,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        parsed_keys, num_keys = utils.parse_keys(keys)
        data = f"unStakeNodes{parsed_keys}"

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.UNSTAKE, num_keys)

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def create_transaction_for_unstaking_tokens(
        self,
        sender: IAccount,
        value: int,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        data = f"unStakeTokens@{self.serializer.serialize([BigUIntValue(value)])}"

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.UNSTAKE_TOKENS)

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def create_transaction_for_unbonding_nodes(
        self,
        sender: IAccount,
        keys: str,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        parsed_keys, num_keys = utils.parse_keys(keys)
        data = f"unBondNodes{parsed_keys}"

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.UNBOND, num_keys)

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def create_transaction_for_unbonding_tokens(
        self,
        sender: IAccount,
        value: int,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        data = f"unBondTokens@{self.serializer.serialize([BigUIntValue(value)])}"

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.UNBOND_TOKENS)

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def create_transaction_for_cleaning_registered_data(
        self,
        sender: IAccount,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        data = "cleanRegisteredData"

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.CLEAN_REGISTERED_DATA)

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def create_transaction_for_restaking_unstaked_nodes(
        self,
        sender: IAccount,
        keys: str,
        native_amount: int,
        estimate_gas: bool,
        gas_limit: int,
        gas_price: int,
        nonce: int,
        version: int,
        options: int,
        guardian_account: Optional[IAccount] = None,
        guardian_address: Optional[Address] = None,
        relayer_account: Optional[IAccount] = None,
        relayer_address: Optional[Address] = None,
        guardian_service_url: str = "",
        guardian_2fa_code: str = "",
    ) -> Transaction:
        parsed_keys, num_keys = utils.parse_keys(keys)
        data = f"reStakeUnStakedNodes{parsed_keys}"

        if estimate_gas:
            gas_limit = self.estimate_system_sc_call(data, MetaChainSystemSCsCost.RE_STAKE_UNSTAKED_NODES, num_keys)

        receiver = Address.new_from_hex(VALIDATORS_SMART_CONTRACT_ADDRESS_HEX, get_address_hrp())

        return self.transactions_controller.create_transaction(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            gas_limt=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            version=version,
            options=options,
            data=data,
            guardian_account=guardian_account,
            guardian_address=guardian_address,
            relayer_account=relayer_account,
            relayer_address=relayer_address,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
        )

    def estimate_system_sc_call(self, transaction_data: str, base_cost: int, factor: int = 1):
        num_bytes = len(transaction_data)
        gas_limit = MIN_GAS_LIMIT + num_bytes * GAS_PER_DATA_BYTE
        gas_limit += factor * base_cost
        return gas_limit
