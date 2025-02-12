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
    Token,
    TokenComputer,
    TokenTransfer,
    Transaction,
    TransactionOnNetwork,
    TransactionsFactoryConfig,
)
from multiversx_sdk.abi import (
    Abi,
    AddressValue,
    BigUIntValue,
    BoolValue,
    BytesValue,
    StringValue,
)

from multiversx_sdk_cli import errors
from multiversx_sdk_cli.base_transactions_controller import BaseTransactionsController
from multiversx_sdk_cli.config import get_address_hrp
from multiversx_sdk_cli.interfaces import IAccount

logger = logging.getLogger("contracts")

HEX_PREFIX = "0x"
FALSE_STR_LOWER = "false"
TRUE_STR_LOWER = "true"
STR_PREFIX = "str:"


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
        value: int,
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
        args = arguments if arguments else []
        if should_prepare_args:
            args = self._prepare_args_for_factory(args)

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
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
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
        value: int,
        transfers: Union[list[str], None],
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
        token_transfers = self._prepare_token_transfers(transfers) if transfers else []

        args = arguments if arguments else []
        if should_prepare_args:
            args = self._prepare_args_for_factory(args)

        tx = self._factory.create_transaction_for_execute(
            sender=caller.address,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            native_transfer_amount=value,
            token_transfers=token_transfers,
        )
        tx.nonce = nonce
        tx.version = version
        tx.options = options
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        self.sign_transaction(
            transaction=tx,
            sender=caller,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
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
        value: int,
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
        args = arguments if arguments else []
        if should_prepare_args:
            args = self._prepare_args_for_factory(args)

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
        tx.guardian = guardian_address
        tx.relayer = relayer_address

        self.sign_transaction(
            transaction=tx,
            sender=owner,
            guardian=guardian_account,
            relayer=relayer_account,
            guardian_service_url=guardian_service_url,
            guardian_2fa_code=guardian_2fa_code,
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
            args = self._prepare_args_for_factory(args)

        sc_query_controller = SmartContractController(self._config.chain_id, proxy, self._abi)

        try:
            response = sc_query_controller.query(contract=contract_address, function=function, arguments=args)
        except Exception as e:
            raise errors.QueryContractError("Couldn't query contract: ", e)

        return response

    def _prepare_token_transfers(self, transfers: list[str]) -> list[TokenTransfer]:
        token_computer = TokenComputer()
        token_transfers: list[TokenTransfer] = []

        for i in range(0, len(transfers) - 1, 2):
            identifier = transfers[i]
            amount = int(transfers[i + 1])
            nonce = token_computer.extract_nonce_from_extended_identifier(identifier)

            token = Token(identifier, nonce)
            transfer = TokenTransfer(token, amount)
            token_transfers.append(transfer)

        return token_transfers

    def _prepare_args_for_factory(self, arguments: list[str]) -> list[Any]:
        args: list[Any] = []

        for arg in arguments:
            if arg.startswith(HEX_PREFIX):
                args.append(BytesValue(self._hex_to_bytes(arg)))
            elif arg.isnumeric():
                args.append(BigUIntValue(int(arg)))
            elif arg.startswith(get_address_hrp()):
                args.append(AddressValue.new_from_address(Address.new_from_bech32(arg)))
            elif arg.lower() == FALSE_STR_LOWER:
                args.append(BoolValue(False))
            elif arg.lower() == TRUE_STR_LOWER:
                args.append(BoolValue(True))
            elif arg.startswith(STR_PREFIX):
                args.append(StringValue(arg[len(STR_PREFIX) :]))
            else:
                raise errors.BadUserInput(
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
