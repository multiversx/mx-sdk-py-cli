from typing import Any, List, Protocol

from Cryptodome.Hash import keccak
from multiversx_sdk import (
    Address,
    AddressComputer,
    SmartContractQuery,
    SmartContractQueryResponse,
)

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.config import get_address_hrp
from multiversx_sdk_cli.constants import ADDRESS_ZERO_HEX
from multiversx_sdk_cli.transactions import do_prepare_transaction

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
    args = utils.as_object(args)

    cli_shared.check_guardian_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    args.receiver = dns_address_for_name(args.name).bech32()
    args.data = dns_register_data(args.name)

    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def compute_all_dns_addresses() -> List[Address]:
    addresses: List[Address] = []
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
    name_enc: bytes = str.encode(name)
    return "register@{}".format(name_enc.hex())


def _query_contract(
    contract_address: Address,
    proxy: INetworkProvider,
    function: str,
    args: List[bytes],
) -> SmartContractQueryResponse:
    query = SmartContractQuery(contract=contract_address, function=function, arguments=args)
    return proxy.query_contract(query)
