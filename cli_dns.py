from typing import Any, List
from Cryptodome.Hash import keccak
from prettytable import PrettyTable

from erdpy import cli_shared, utils
from erdpy.contracts import SmartContract
from erdpy.accounts import Account, Address
from erdpy.proxy.core import ElrondProxy
from erdpy.transactions import do_prepare_transaction

MaxNumShards = 256
ShardIdentiferLen = 2
InitialDNSAddress = bytes([1] * 32)


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "dns", "Operations related to the Domain Name Service")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "dns", "dns-addresses", "Lists all 256 DNS contract addresses")
    sub.set_defaults(func=print_dns_addresses_table)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "name-hash", "The hash of a name, as computed by a DNS smart contract")
    _add_name_arg(sub)
    sub.set_defaults(func=name_hash)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "address-for-name", "DNS contract address (bech32) that corresponds to a name")
    _add_name_arg(sub)
    sub.set_defaults(func=dns_address_for_name)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "address-for-name-hex", "DNS contract address (hex) that corresponds to a name")
    _add_name_arg(sub)
    sub.set_defaults(func=dns_address_for_name_hex)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "register", "Send a register transaction to the appropriate DNS contract from given user and with given name")
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_wallet_args(sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(sub, with_receiver=False, with_data=False)
    sub.add_argument("--name", help="the name to register")
    sub.set_defaults(func=dns_register)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_name_arg(sub: Any):
    sub.add_argument("name", help="the name for which to check")


def print_dns_addresses_table(args: Any):
    t = PrettyTable(['Shard ID', 'Contract address (bech32)', 'Contract address (hex)'])
    for i in range(0, 256):
        address = compute_dns_address_for_shard_id(i)
        t.add_row([i, address, address.hex()])
    print(t)


def name_hash(args: Any):
    name = args.name
    name_hash = compute_name_hash(name)
    print(name_hash.hex())


def dns_address_for_name(args: Any):
    name = args.name
    dns_address = compute_dns_address_for_name(name)
    print(dns_address)


def dns_address_for_name_hex(args: Any):
    name = args.name
    dns_address = compute_dns_address_for_name(name)
    print(dns_address.hex())


def dns_register(args: Any):
    args = utils.as_object(args)

    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    args.receiver = compute_dns_address_for_name(args.name).bech32()
    args.data = dns_register_data(args.name)

    tx = do_prepare_transaction(args)

    if hasattr(args, "relay") and args.relay:
        args.outfile.write(tx.serialize_as_inner())
        return

    try:
        if args.send:
            tx.send(ElrondProxy(args.proxy))
        elif args.simulate:
            response = tx.simulate(ElrondProxy(args.proxy))
            utils.dump_out_json(response)
    finally:
        tx.dump_to(args.outfile)


def compute_all_dns_addresses() -> List[Address]:
    addresses = []
    for i in range(0, 256):
        addresses.append(compute_dns_address_for_shard_id(i))
    return addresses


def compute_name_hash(name: str) -> Address:
    return keccak.new(digest_bits=256).update(str.encode(name)).digest()


def compute_dns_address_for_name(name: str) -> Address:
    name_hash = compute_name_hash(name)
    shard_id = name_hash[31]
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
