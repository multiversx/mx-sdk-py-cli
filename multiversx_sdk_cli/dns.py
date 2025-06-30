from typing import Any, Protocol

from Cryptodome.Hash import keccak
from multiversx_sdk import (
    Address,
    AddressComputer,
    SmartContractQuery,
    SmartContractQueryResponse,
)

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.args_validation import (
    validate_broadcast_args,
    validate_chain_id_args,
    validate_transaction_args,
)
from multiversx_sdk_cli.config_env import get_address_hrp
from multiversx_sdk_cli.constants import ADDRESS_ZERO_HEX
from multiversx_sdk_cli.transactions import TransactionsController

MaxNumShards = 256
ShardIdentiferLen = 2
InitialDNSAddress = bytes([1] * 32)


# fmt: off
class INetworkProvider(Protocol):
    def query_contract(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        ...
# fmt: on


def resolve(name: str, proxy: INetworkProvider) -> Address:
    dns_address = dns_address_for_name(name)

    response = _query_contract(contract_address=dns_address, proxy=proxy, function="resolve", args=[name.encode()])

    if len(response.return_data_parts) == 0:
        return Address.new_from_hex(ADDRESS_ZERO_HEX, get_address_hrp())

    result = response.return_data_parts[0]
    return Address(result, get_address_hrp())


def validate_name(name: str, shard_id: int, proxy: INetworkProvider):
    dns_address = compute_dns_address_for_shard_id(shard_id)

    response = _query_contract(
        contract_address=dns_address,
        proxy=proxy,
        function="validateName",
        args=[name.encode()],
    )

    return_code: str = response.return_code
    if return_code == "ok":
        print(f"name [{name}] is valid")
    else:
        print(f"name [{name}] is invalid")


def register(args: Any):
    validate_transaction_args(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    native_amount = int(args.value)

    receiver = dns_address_for_name(args.name)
    data = dns_register_data(args.name)

    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    controller = TransactionsController(chain_id)

    tx = controller.create_transaction(
        sender=sender,
        receiver=receiver,
        native_amount=native_amount,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        nonce=sender.nonce,
        version=args.version,
        options=args.options,
        data=data,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def compute_all_dns_addresses() -> list[Address]:
    addresses: list[Address] = []
    for i in range(0, 256):
        addresses.append(compute_dns_address_for_shard_id(i))
    return addresses


def name_hash(name: str) -> bytes:
    return keccak.new(digest_bits=256).update(str.encode(name)).digest()


def registration_cost(shard_id: int, proxy: INetworkProvider) -> int:
    dns_address = compute_dns_address_for_shard_id(shard_id)

    response = _query_contract(
        contract_address=dns_address,
        proxy=proxy,
        function="getRegistrationCost",
        args=[],
    )

    data = response.return_data_parts[0]
    if not data:
        return 0
    else:
        return int.from_bytes(data, byteorder="big", signed=False)


def version(shard_id: int, proxy: INetworkProvider) -> str:
    dns_address = compute_dns_address_for_shard_id(shard_id)

    response = _query_contract(contract_address=dns_address, proxy=proxy, function="version", args=[])
    return response.return_data_parts[0].decode()


def dns_address_for_name(name: str) -> Address:
    hash = name_hash(name)
    shard_id = hash[31]
    return compute_dns_address_for_shard_id(shard_id)


def compute_dns_address_for_shard_id(shard_id: int) -> Address:
    deployer_pubkey_prefix = InitialDNSAddress[: len(InitialDNSAddress) - ShardIdentiferLen]

    deployer_pubkey = deployer_pubkey_prefix + bytes([0, shard_id])
    deployer = Address(deployer_pubkey, get_address_hrp())
    nonce = 0
    address_computer = AddressComputer(number_of_shards=3)
    contract_address = address_computer.compute_contract_address(deployer, nonce)
    return contract_address


def dns_register_data(name: str) -> str:
    name_as_hex = str.encode(name).hex()
    return f"register@{name_as_hex}"


def _query_contract(
    contract_address: Address,
    proxy: INetworkProvider,
    function: str,
    args: list[bytes],
) -> SmartContractQueryResponse:
    query = SmartContractQuery(contract=contract_address, function=function, arguments=args)
    return proxy.query_contract(query)
