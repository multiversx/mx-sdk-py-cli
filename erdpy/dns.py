from typing import Any, List

from Cryptodome.Hash import keccak

from erdpy import cli_shared, utils
from erdpy.accounts import Account, Address
from erdpy.contracts import SmartContract
from erdpy.proxy.core import ElrondProxy
from erdpy.transactions import do_prepare_transaction
from erdpy.interfaces import IElrondProxy

MaxNumShards = 256
ShardIdentiferLen = 2
InitialDNSAddress = bytes([1] * 32)


def resolve(name: str, proxy: ElrondProxy) -> Address:
    name_arg = "0x{}".format(str.encode(name).hex())
    dns_address = dns_address_for_name(name)
    contract = SmartContract(dns_address)
    result = contract.query(proxy, "resolve", [name_arg])
    if len(result) == 0:
        return Address.zero()
    return Address(result[0].hex)


def validate_name(name: str, shard_id: int, proxy: ElrondProxy):
    name_arg = "0x{}".format(str.encode(name).hex())
    dns_address = compute_dns_address_for_shard_id(shard_id)
    contract = SmartContract(dns_address)
    contract.query(proxy, "validateName", [name_arg])


def register(args: Any):
    args = utils.as_object(args)

    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    args.receiver = dns_address_for_name(args.name).bech32()
    args.data = dns_register_data(args.name)

    tx = do_prepare_transaction(args)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(tx.serialize_as_inner())
        return

    cli_shared.send_or_simulate(tx, args)


def compute_all_dns_addresses() -> List[Address]:
    addresses = []
    for i in range(0, 256):
        addresses.append(compute_dns_address_for_shard_id(i))
    return addresses


def name_hash(name: str) -> bytes:
    return keccak.new(digest_bits=256).update(str.encode(name)).digest()


def registration_cost(shard_id: int, proxy: ElrondProxy) -> int:
    dns_address = compute_dns_address_for_shard_id(shard_id)
    contract = SmartContract(dns_address)
    result = contract.query(proxy, "getRegistrationCost", [])
    if len(result[0]) == 0:
        return 0
    else:
        return int("0x{}".format(result[0]))


def version(shard_id: int, proxy: IElrondProxy) -> str:
    dns_address = compute_dns_address_for_shard_id(shard_id)
    contract = SmartContract(dns_address)
    result = contract.query(proxy, "version", [])
    return bytearray.fromhex(result[0].hex).decode()


def dns_address_for_name(name: str) -> Address:
    hash = name_hash(name)
    shard_id = hash[31]
    return compute_dns_address_for_shard_id(shard_id)


def compute_dns_address_for_shard_id(shard_id) -> Address:
    deployer_pubkey_prefix = InitialDNSAddress[:len(InitialDNSAddress) - ShardIdentiferLen]

    deployer_pubkey = deployer_pubkey_prefix + bytes([0, shard_id])
    deployer = Account(address=Address(deployer_pubkey))
    deployer.nonce = 0
    # Workaround: currently, in erdpy, in order to compute the address of a contract, one has to create an instance of the class "SmartContract".
    # This might change in the future.
    contract = SmartContract()
    contract.owner = deployer
    contract.compute_address()
    return contract.address


def dns_register_data(name: str) -> str:
    name_enc: bytes = str.encode(name)
    return "register@{}".format(name_enc.hex())
