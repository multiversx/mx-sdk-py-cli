from typing import Any, List, Protocol

from Cryptodome.Hash import keccak
from multiversx_sdk import Address, AddressComputer, TransactionsFactoryConfig
from multiversx_sdk.network_providers.network_config import NetworkConfig

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.constants import ADDRESS_ZERO_BECH32, DEFAULT_HRP
from multiversx_sdk_cli.contracts import SmartContract
from multiversx_sdk_cli.transactions import (compute_relayed_v1_data,
                                             do_prepare_transaction)

MaxNumShards = 256
ShardIdentiferLen = 2
InitialDNSAddress = bytes([1] * 32)


class INetworkProvider(Protocol):
    def query_contract(self, query: Any) -> Any:
        ...

    def get_network_config(self) -> NetworkConfig:
        ...


def resolve(name: str, proxy: INetworkProvider) -> Address:
    name_arg = "0x{}".format(str.encode(name).hex())
    dns_address = dns_address_for_name(name)

    response = _query_contract(
        contract_address=dns_address,
        proxy=proxy,
        function="resolve",
        args=[name_arg]
    )

    if len(response) == 0:
        return Address.from_bech32(ADDRESS_ZERO_BECH32)

    result = response[0].get("returnDataParts")[0]
    return Address.from_hex(result, DEFAULT_HRP)


def validate_name(name: str, shard_id: int, proxy: INetworkProvider):
    name_arg = "0x{}".format(str.encode(name).hex())
    dns_address = compute_dns_address_for_shard_id(shard_id)

    response = _query_contract(
        contract_address=dns_address,
        proxy=proxy,
        function="validateName",
        args=[name_arg]
    )

    response = response[0]

    return_code = response["returnCode"]
    if return_code == "ok":
        print(f"name [{name}] is valid")
    else:
        print(f"name [{name}] is invalid")

    print(response)


def register(args: Any):
    args = utils.as_object(args)

    cli_shared.check_guardian_and_options_args(args)
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    cli_shared.prepare_chain_id_in_args(args)
    args.receiver = dns_address_for_name(args.name).bech32()
    args.data = dns_register_data(args.name)

    tx = do_prepare_transaction(args)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(compute_relayed_v1_data(tx))
        return

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
        args=[]
    )

    response = response[0]

    data = response["returnDataParts"][0]
    if not data:
        return 0
    else:
        return int("0x{}".format(data))


def version(shard_id: int, proxy: INetworkProvider) -> str:
    dns_address = compute_dns_address_for_shard_id(shard_id)

    response = _query_contract(
        contract_address=dns_address,
        proxy=proxy,
        function="version",
        args=[]
    )

    response = response[0]
    return bytearray.fromhex(response["returnDataParts"][0]).decode()


def dns_address_for_name(name: str) -> Address:
    hash = name_hash(name)
    shard_id = hash[31]
    return compute_dns_address_for_shard_id(shard_id)


def compute_dns_address_for_shard_id(shard_id: int) -> Address:
    deployer_pubkey_prefix = InitialDNSAddress[:len(InitialDNSAddress) - ShardIdentiferLen]

    deployer_pubkey = deployer_pubkey_prefix + bytes([0, shard_id])
    deployer = Account(address=Address(deployer_pubkey, DEFAULT_HRP))
    deployer.nonce = 0
    address_computer = AddressComputer(number_of_shards=3)
    contract_address = address_computer.compute_contract_address(deployer.address, deployer.nonce)
    return contract_address


def dns_register_data(name: str) -> str:
    name_enc: bytes = str.encode(name)
    return "register@{}".format(name_enc.hex())


def _query_contract(contract_address: Address, proxy: INetworkProvider, function: str, args: List[Any]) -> List[Any]:
    chain_id = proxy.get_network_config().chain_id
    config = TransactionsFactoryConfig(chain_id)
    contract = SmartContract(config)

    return contract.query_contract(
        contract_address=contract_address,
        proxy=proxy,
        function=function,
        arguments=args,
        should_prepare_args=False
    )
