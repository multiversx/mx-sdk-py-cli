import logging
from typing import Any, Optional, Union

from multiversx_sdk import Address, LedgerAccount, Transaction, TransactionComputer
from multiversx_sdk.abi import (
    AddressValue,
    BigUIntValue,
    BoolValue,
    BytesValue,
    StringValue,
)

from multiversx_sdk_cli.config_env import get_address_hrp
from multiversx_sdk_cli.constants import (
    ADDRESS_PREFIX,
    EXTRA_GAS_LIMIT_FOR_GUARDED_TRANSACTIONS,
    EXTRA_GAS_LIMIT_FOR_RELAYED_TRANSACTIONS,
    FALSE_STR_LOWER,
    HEX_PREFIX,
    MAINCHAIN_ADDRESS_HRP,
    STR_PREFIX,
    TRUE_STR_LOWER,
)
from multiversx_sdk_cli.cosign_transaction import cosign_transaction
from multiversx_sdk_cli.errors import BadUserInput, TransactionSigningError
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.interfaces import IAccount

logger = logging.getLogger("base_controller")


class BaseTransactionsController:
    def __init__(self) -> None:
        pass

    def sign_transaction(
        self,
        transaction: Transaction,
        sender: Optional[IAccount] = None,
        guardian: Optional[IAccount] = None,
        relayer: Optional[IAccount] = None,
        guardian_service_url: Optional[str] = None,
        guardian_2fa_code: Optional[str] = None,
    ):
        """Signs the transaction using the sender's account and, if required, additionally signs with the guardian's and relayer's accounts. Ensures the appropriate transaction options are set as needed."""
        self._set_options_for_guarded_transaction_if_needed(transaction)
        self._set_options_for_hash_signing_if_needed(transaction, sender, guardian, relayer)

        if sender:
            try:
                transaction.signature = sender.sign_transaction(transaction)
            except Exception as e:
                raise TransactionSigningError(f"Could not sign transaction: {str(e)}")

        self._sign_guarded_transaction_if_guardian(
            transaction,
            guardian,
            guardian_service_url,
            guardian_2fa_code,
        )
        self._sign_relayed_transaction_if_relayer(transaction, relayer)

    def add_extra_gas_limit_if_required(self, transaction: Transaction):
        """In case of guarded or relayed transactions, extra gas limit is added."""
        if transaction.guardian:
            transaction.gas_limit += EXTRA_GAS_LIMIT_FOR_GUARDED_TRANSACTIONS

        if transaction.relayer:
            transaction.gas_limit += EXTRA_GAS_LIMIT_FOR_RELAYED_TRANSACTIONS

    def _set_options_for_guarded_transaction_if_needed(self, transaction: Transaction):
        if transaction.guardian:
            transaction_computer = TransactionComputer()
            transaction_computer.apply_guardian(transaction, transaction.guardian)

    def _set_options_for_hash_signing_if_needed(
        self,
        transaction: Transaction,
        sender: Union[IAccount, None],
        guardian: Union[IAccount, None],
        relayer: Union[IAccount, None],
    ):
        if (
            isinstance(sender, LedgerAccount)
            or isinstance(guardian, LedgerAccount)
            or isinstance(relayer, LedgerAccount)
        ):
            transaction_computer = TransactionComputer()
            transaction_computer.apply_options_for_hash_signing(transaction)

    def _sign_guarded_transaction_if_guardian(
        self,
        transaction: Transaction,
        guardian: Union[IAccount, None],
        guardian_service_url: Union[str, None],
        guardian_2fa_code: Union[str, None],
    ) -> Transaction:
        #  If the guardian account is provided, we sign locally. Otherwise, we reach for the trusted cosign service.
        if guardian:
            try:
                transaction.guardian_signature = guardian.sign_transaction(transaction)
            except Exception as e:
                raise TransactionSigningError(f"Could not sign transaction: {str(e)}")
        elif transaction.guardian and guardian_service_url and guardian_2fa_code:
            cosign_transaction(transaction, guardian_service_url, guardian_2fa_code)

        return transaction

    def _sign_relayed_transaction_if_relayer(self, transaction: Transaction, relayer: Union[IAccount, None]):
        if relayer and transaction.relayer:
            try:
                transaction.relayer_signature = relayer.sign_transaction(transaction)
            except Exception as e:
                raise TransactionSigningError(f"Could not sign transaction: {str(e)}")

    def _convert_args_to_typed_values(self, arguments: list[str]) -> list[Any]:
        args: list[Any] = []

        for arg in arguments:
            if arg.startswith(HEX_PREFIX):
                args.append(BytesValue(self._hex_to_bytes(arg)))
            elif arg.isnumeric():
                args.append(BigUIntValue(int(arg)))
            elif arg.startswith(ADDRESS_PREFIX):
                args.append(AddressValue.new_from_address(Address.new_from_bech32(arg[len(ADDRESS_PREFIX) :])))
            elif arg.startswith(MAINCHAIN_ADDRESS_HRP):
                # this flow will be removed in the future
                logger.warning(
                    "Address argument has no prefix. This flow will be removed in the future. Please provide each address using the `addr:` prefix. (e.g. --arguments addr:erd1...)"
                )
                args.append(AddressValue.new_from_address(Address.new_from_bech32(arg)))
            elif arg.startswith(get_address_hrp()):
                args.append(AddressValue.new_from_address(Address.new_from_bech32(arg)))
            elif arg.lower() == FALSE_STR_LOWER:
                args.append(BoolValue(False))
            elif arg.lower() == TRUE_STR_LOWER:
                args.append(BoolValue(True))
            elif arg.startswith(STR_PREFIX):
                args.append(StringValue(arg[len(STR_PREFIX) :]))
            else:
                raise BadUserInput(
                    f"Unknown argument type for argument: `{arg}`. Use `mxpy contract <sub-command> --help` to check all supported arguments"
                )

        return args

    def _hex_to_bytes(self, arg: str):
        argument = arg[len(HEX_PREFIX) :]
        argument = argument.upper()
        argument = self.ensure_even_length(argument)
        return bytes.fromhex(argument)

    def ensure_even_length(self, string: str) -> str:
        if len(string) % 2 == 1:
            return "0" + string
        return string

    def _set_transaction_fields(
        self,
        transaction: Transaction,
        nonce: int,
        version: int,
        options: int,
        gas_price: int,
        guardian_and_relayer_data: GuardianRelayerData,
    ):
        transaction.nonce = nonce
        transaction.version = version
        transaction.options = options
        transaction.gas_price = gas_price
        transaction.guardian = guardian_and_relayer_data.guardian_address
        transaction.relayer = guardian_and_relayer_data.relayer_address
