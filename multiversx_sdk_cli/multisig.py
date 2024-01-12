from typing import List, Union

from multiversx_sdk_core import (Address, TokenComputer, TokenTransfer,
                                 Transaction)
from multiversx_sdk_core.transaction_factories.token_transfers_data_builder import \
    TokenTransfersDataBuilder
from multiversx_sdk_core.transaction_factories.transactions_factory_config import \
    TransactionsFactoryConfig

from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.contracts import SmartContract


def prepare_transaction_for_egld_transfer(sender: Account,
                                          multisig: str,
                                          receiver: str,
                                          chain_id: str,
                                          value: int,
                                          gas_limit: int,
                                          nonce: int,
                                          version: int,
                                          options: int,
                                          guardian: str) -> Transaction:
    config = TransactionsFactoryConfig(chain_id)
    contract = SmartContract(config)

    return contract.prepare_execute_transaction(
        caller=sender,
        contract=Address.from_bech32(multisig),
        function="proposeTransferExecute",
        arguments=[f"{receiver}", f"{value}"],
        gas_limit=gas_limit,
        value=0,
        transfers=None,
        nonce=nonce,
        version=version,
        options=options,
        guardian=guardian)


def prepare_transaction_for_custom_token_transfer(sender: Account,
                                                  multisig: str,
                                                  receiver: str,
                                                  chain_id: str,
                                                  transfers: List[str],
                                                  gas_limit: int,
                                                  nonce: int,
                                                  version: int,
                                                  options: int,
                                                  guardian: str) -> Transaction:
    config = TransactionsFactoryConfig(chain_id)
    contract = SmartContract(config)

    token_transfers = contract.prepare_token_transfers(transfers)
    transfer_receiver = Address.from_bech32(receiver)
    transfer_data_parts = _prepare_data_parts_for_multisig_transfer(transfer_receiver, token_transfers)
    multisig_contract = Address.from_bech32(multisig)

    arguments: List[str] = [transfer_receiver.to_hex(), "00"]
    if transfer_data_parts[0] != "ESDTTransfer":
        arguments[0] = multisig_contract.to_hex()

    transfer_data_parts[0] = transfer_data_parts[0].encode().hex()
    arguments.extend(transfer_data_parts)

    tx = contract.prepare_execute_transaction(
        caller=sender,
        contract=multisig_contract,
        function="proposeAsyncCall",
        arguments=None,
        gas_limit=gas_limit,
        value=0,
        transfers=None,
        nonce=nonce,
        version=version,
        options=options,
        guardian=guardian)

    data_field = tx.data.decode() + "@" + _build_data_payload(arguments)
    tx.data = data_field.encode()
    tx.signature = bytes.fromhex(sender.sign_transaction(tx))
    return tx


def prepare_transaction_for_depositing_funds(sender: Account,
                                             multisig: str,
                                             chain_id: str,
                                             value: int,
                                             transfers: Union[List[str], None],
                                             gas_limit: int,
                                             nonce: int,
                                             version: int,
                                             options: int,
                                             guardian: str):
    config = TransactionsFactoryConfig(chain_id)
    contract = SmartContract(config)

    return contract.prepare_execute_transaction(
        caller=sender,
        contract=Address.from_bech32(multisig),
        function="deposit",
        arguments=None,
        gas_limit=gas_limit,
        value=value,
        transfers=transfers,
        nonce=nonce,
        version=version,
        options=options,
        guardian=guardian
    )


def _prepare_data_parts_for_multisig_transfer(receiver: Address, token_transfers: List[TokenTransfer]):
    token_computer = TokenComputer()
    data_builder = TokenTransfersDataBuilder(token_computer)
    data_parts: List[str] = []

    if len(token_transfers) == 1:
        transfer = token_transfers[0]
        if token_computer.is_fungible(transfer.token):
            data_parts = data_builder.build_args_for_esdt_transfer(transfer=transfer)
        else:
            data_parts = data_builder.build_args_for_single_esdt_nft_transfer(transfer=transfer, receiver=receiver)
    elif len(token_transfers) > 1:
        data_parts = data_builder.build_args_for_multi_esdt_nft_transfer(receiver=receiver, transfers=token_transfers)

    return data_parts


def _build_data_payload(parts: List[str]) -> str:
    return "@".join(parts)
