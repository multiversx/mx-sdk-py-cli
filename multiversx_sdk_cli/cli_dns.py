from typing import Any, List

from multiversx_sdk import ProxyNetworkProvider
from rich.console import Console
from rich.table import Table

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.config import get_config_for_network_providers
from multiversx_sdk_cli.constants import ADDRESS_ZERO_HEX
from multiversx_sdk_cli.dns import (
    compute_dns_address_for_shard_id,
    dns_address_for_name,
    name_hash,
    register,
    registration_cost,
    resolve,
    validate_name,
    version,
)
from multiversx_sdk_cli.errors import ArgumentsNotProvidedError


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "dns", "Operations related to the Domain Name Service")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(
        subparsers,
        "dns",
        "register",
        "Send a register transaction to the appropriate DNS contract from given user and with given name",
    )
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)
    sub.add_argument("--name", help="the name to register")
    sub.set_defaults(func=register)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "resolve", "Find the address for a name")
    _add_name_arg(sub)
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=dns_resolve)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "dns",
        "validate-name",
        "Asks one of the DNS contracts to validate a name. Can be useful before registering it.",
    )
    _add_name_arg(sub)
    sub.add_argument(
        "--shard-id",
        type=int,
        default=0,
        help="shard id of the contract to call (default: %(default)s)",
    )
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=dns_validate_name)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "dns",
        "name-hash",
        "The hash of a name, as computed by a DNS smart contract",
    )
    _add_name_arg(sub)
    sub.set_defaults(func=get_name_hash)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "dns",
        "registration-cost",
        "Gets the registration cost from a DNS smart contract, by default the one with shard id 0.",
    )
    sub.add_argument(
        "--shard-id",
        type=int,
        default=0,
        help="shard id of the contract to call (default: %(default)s)",
    )
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_registration_cost)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "version", "Asks the contract for its version")
    sub.add_argument(
        "--shard-id",
        type=int,
        default=0,
        help="shard id of the contract to call (default: %(default)s)",
    )
    sub.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="prints a list of all DNS contracts and their current versions (default: %(default)s)",
    )
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_version)

    sub = cli_shared.add_command_subparser(subparsers, "dns", "dns-addresses", "Lists all 256 DNS contract addresses")
    sub.set_defaults(func=print_dns_addresses_table)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "dns",
        "dns-address-for-name",
        "DNS contract address (bech32) that corresponds to a name",
    )
    _add_name_arg(sub)
    sub.set_defaults(func=get_dns_address_for_name)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "dns",
        "dns-address-for-name-hex",
        "DNS contract address (hex) that corresponds to a name",
    )
    _add_name_arg(sub)
    sub.set_defaults(func=get_dns_address_for_name_hex)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_name_arg(sub: Any):
    sub.add_argument("name", help="the name for which to check")


def _ensure_proxy_is_provided(args: Any):
    if not args.proxy:
        raise ArgumentsNotProvidedError("'--proxy' argument not provided")


def dns_resolve(args: Any):
    _ensure_proxy_is_provided(args)

    config = get_config_for_network_providers()
    addr = resolve(args.name, ProxyNetworkProvider(url=args.proxy, config=config))
    if addr.to_hex() != ADDRESS_ZERO_HEX:
        print(addr.to_bech32())


def dns_validate_name(args: Any):
    _ensure_proxy_is_provided(args)

    config = get_config_for_network_providers()
    validate_name(args.name, args.shard_id, ProxyNetworkProvider(url=args.proxy, config=config))


def get_name_hash(args: Any):
    print(name_hash(args.name).hex())


def get_dns_address_for_name(args: Any):
    name = args.name
    dns_address = dns_address_for_name(name)
    print(dns_address.to_bech32())


def get_dns_address_for_name_hex(args: Any):
    name = args.name
    dns_address = dns_address_for_name(name)
    print(dns_address.to_hex())


def get_registration_cost(args: Any):
    _ensure_proxy_is_provided(args)

    config = get_config_for_network_providers()
    print(registration_cost(args.shard_id, ProxyNetworkProvider(url=args.proxy, config=config)))


def get_version(args: Any):
    _ensure_proxy_is_provided(args)

    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    if args.all:
        table = Table(title="DNS Version")
        table.add_column("Shard ID")
        table.add_column("Contract address (bech32)")
        table.add_column("Contract address (hex)")
        table.add_column("Version")

        for shard_id in range(0, 256):
            address = compute_dns_address_for_shard_id(shard_id)
            v = version(shard_id, proxy)
            table.add_row(str(shard_id), address.to_bech32(), address.to_hex(), v)

        console = Console()
        console.print(table)
    else:
        shard_id = int(args.shard_id)
        print(version(shard_id, proxy))


def print_dns_addresses_table(args: Any):
    table = Table(title="DNS Addresses")

    table.add_column("Shard ID")
    table.add_column("Contract address (bech32)")
    table.add_column("Contract address (hex)")

    for shard_id in range(0, 256):
        address = compute_dns_address_for_shard_id(shard_id)
        table.add_row(str(shard_id), address.to_bech32(), address.to_hex())

    console = Console()
    console.print(table)
