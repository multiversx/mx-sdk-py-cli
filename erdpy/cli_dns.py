from typing import Any, List
from prettytable import PrettyTable

from erdpy import cli_shared
from erdpy.dns import name_hash, dns_address_for_name, register, resolve, registration_cost, validate_name, version, compute_dns_address_for_shard_id
from erdpy.accounts import Address
from erdpy.proxy.core import ElrondProxy


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "dns", "Operations related to the Domain Name Service")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "dns", "register", "Send a register transaction to the appropriate DNS contract from given user and with given name")
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_broadcast_args(sub, relay=True)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    sub.add_argument("--name", help="the name to register")
    sub.set_defaults(func=register)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "resolve", "Find the address for a name")
    _add_name_arg(sub)
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=dns_resolve)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "validate-name", "Asks one of the DNS contracts to validate a name. Can be useful before registering it.")
    _add_name_arg(sub)
    sub.add_argument("--shard-id", default=0, help="shard id of the contract to call (default: %(default)s)")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=dns_validate_name)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "name-hash", "The hash of a name, as computed by a DNS smart contract")
    _add_name_arg(sub)
    sub.set_defaults(func=get_name_hash)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "registration-cost", "Gets the registration cost from a DNS smart contract, by default the one with shard id 0.")
    sub.add_argument("--shard-id", default=0, help="shard id of the contract to call (default: %(default)s)")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_registration_cost)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "version", "Asks the contract for its version")
    sub.add_argument("--shard-id", default=0, help="shard id of the contract to call (default: %(default)s)")
    sub.add_argument("--all", action="store_true", default=False, help="prints a list of all DNS contracts and their current versions (default: %(default)s)")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_version)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "dns-addresses", "Lists all 256 DNS contract addresses")
    sub.set_defaults(func=print_dns_addresses_table)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "dns-address-for-name", "DNS contract address (bech32) that corresponds to a name")
    _add_name_arg(sub)
    sub.set_defaults(func=get_dns_address_for_name)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "dns-address-for-name-hex", "DNS contract address (hex) that corresponds to a name")
    _add_name_arg(sub)
    sub.set_defaults(func=get_dns_address_for_name_hex)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_name_arg(sub: Any):
    sub.add_argument("name", help="the name for which to check")


def dns_resolve(args: Any):
    addr = resolve(args.name, ElrondProxy(args.proxy))
    if addr.hex() != Address.zero().hex():
        print(addr.bech32())


def dns_validate_name(args: Any):
    validate_name(args.name, args.shard_id, ElrondProxy(args.proxy))


def get_name_hash(args: Any):
    print(name_hash(args.name).hex())


def get_dns_address_for_name(args: Any):
    name = args.name
    dns_address = dns_address_for_name(name)
    print(dns_address)


def get_dns_address_for_name_hex(args: Any):
    name = args.name
    dns_address = dns_address_for_name(name)
    print(dns_address.hex())


def get_registration_cost(args: Any):
    print(registration_cost(args.shard_id, ElrondProxy(args.proxy)))


def get_version(args: Any):
    proxy = ElrondProxy(args.proxy)
    if args.all:
        t = PrettyTable(['Shard ID', 'Contract address (bech32)', 'Contract address (hex)', 'Version'])
        for shard_id in range(0, 256):
            address = compute_dns_address_for_shard_id(shard_id)
            v = version(shard_id, proxy)
            t.add_row([shard_id, address, address.hex(), v])
        print(t)
    else:
        shard_id = int(args.shard_id)
        print(version(shard_id, proxy))


def print_dns_addresses_table(args: Any):
    t = PrettyTable(['Shard ID', 'Contract address (bech32)', 'Contract address (hex)'])
    for shard_id in range(0, 256):
        address = compute_dns_address_for_shard_id(shard_id)
        t.add_row([shard_id, address, address.hex()])
    print(t)
