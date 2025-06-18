import logging
from typing import Any, Optional

from multiversx_sdk import Address
from multiversx_sdk import NetworkProviderError as SDKNetworkProviderError
from multiversx_sdk import ProxyNetworkProvider, Token, TokenComputer

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.config import get_config_for_network_providers
from multiversx_sdk_cli.env import MxpyEnv
from multiversx_sdk_cli.errors import (
    ArgumentsNotProvidedError,
    BadUsage,
    NetworkProviderError,
)
from multiversx_sdk_cli.utils import dump_out_json

logger = logging.getLogger("cli.get")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "get", "Get info from the network.")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "get", "account", "Get info about an account.")
    _add_alias_arg(sub)
    _add_address_arg(sub)
    _add_proxy_arg(sub)
    sub.add_argument(
        "--balance",
        action="store_true",
        default=False,
        required=False,
        help="whether to only fetch the balance of the address",
    )
    sub.set_defaults(func=get_account)

    sub = cli_shared.add_command_subparser(
        subparsers, "get", "storage", "Get the storage (key-value pairs) of an account."
    )
    _add_alias_arg(sub)
    _add_address_arg(sub)
    _add_proxy_arg(sub)
    sub.set_defaults(func=get_storage)

    sub = cli_shared.add_command_subparser(
        subparsers, "get", "storage-entry", "Get a specific storage entry (key-value pair) of an account."
    )
    _add_alias_arg(sub)
    _add_address_arg(sub)
    _add_proxy_arg(sub)
    sub.add_argument("--key", type=str, required=True, help="the storage key to read from")
    sub.set_defaults(func=get_key)

    sub = cli_shared.add_command_subparser(subparsers, "get", "token", "Get a token of an account.")
    _add_alias_arg(sub)
    _add_address_arg(sub)
    _add_proxy_arg(sub)
    sub.add_argument(
        "--identifier",
        type=str,
        required=True,
        help="the token identifier. Works for ESDT and NFT. (e.g. FNG-123456, NFT-987654-0a)",
    )
    sub.set_defaults(func=get_token)

    sub = cli_shared.add_command_subparser(subparsers, "get", "transaction", "Get a transaction from the network.")
    _add_proxy_arg(sub)
    sub.add_argument("--hash", type=str, required=True, help="the transaction hash")
    sub.set_defaults(func=get_transaction)

    sub = cli_shared.add_command_subparser(subparsers, "get", "network-config", "Get the network configuration.")
    _add_proxy_arg(sub)
    sub.set_defaults(func=get_network_config)

    sub = cli_shared.add_command_subparser(subparsers, "get", "network-status", "Get the network status.")
    _add_proxy_arg(sub)
    sub.add_argument(
        "--shard",
        type=int,
        choices=[0, 1, 2, 4294967295],
        default=4294967295,
        help="the shard to get the status for (default: %(default)s, which is methachain)",
    )
    sub.set_defaults(func=get_network_status)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_alias_arg(sub: Any):
    sub.add_argument("--alias", type=str, help="the alias of the wallet if configured in address config")


def _add_address_arg(sub: Any):
    sub.add_argument("--address", type=str, help="the bech32 address")


def _add_proxy_arg(sub: Any):
    sub.add_argument("--proxy", type=str, help="the proxy url")


def get_account(args: Any):
    if args.alias and args.address:
        raise BadUsage("Provide either '--alias' or '--address'")

    if args.address:
        address = Address.new_from_bech32(args.address)
    else:
        hrp = cli_shared._get_address_hrp(args)
        address = _get_address_from_alias_or_config(args.alias, hrp)

    proxy = _get_proxy(args)

    logger.info(f"Fetching details about {address.to_bech32()}")
    response = proxy.get_account(address)

    if args.balance:
        print(response.balance)
    else:
        dump_out_json(response.raw)


def get_storage(args: Any):
    if args.alias and args.address:
        raise BadUsage("Provide either '--alias' or '--address'")

    if args.address:
        address = Address.new_from_bech32(args.address)
    else:
        hrp = cli_shared._get_address_hrp(args)
        address = _get_address_from_alias_or_config(args.alias, hrp)

    proxy = _get_proxy(args)

    logger.info(f"Fetching details about {address.to_bech32()}")
    response = proxy.get_account_storage(address)

    dump_out_json(response.raw)


def get_key(args: Any):
    if args.alias and args.address:
        raise BadUsage("Provide either '--alias' or '--address'")

    if args.address:
        address = Address.new_from_bech32(args.address)
    else:
        hrp = cli_shared._get_address_hrp(args)
        address = _get_address_from_alias_or_config(args.alias, hrp)

    proxy = _get_proxy(args)

    logger.info(f"Fetching details about {address.to_bech32()}")
    try:
        response = proxy.get_account_storage_entry(address, args.key)
    except SDKNetworkProviderError as e:
        raise NetworkProviderError(e.url, e.data)

    dump_out_json(response.raw)


def get_token(args: Any):
    if args.alias and args.address:
        raise BadUsage("Provide either '--alias' or '--address'")

    if args.address:
        address = Address.new_from_bech32(args.address)
    else:
        hrp = cli_shared._get_address_hrp(args)
        address = _get_address_from_alias_or_config(args.alias, hrp)

    proxy = _get_proxy(args)

    logger.info(f"Fetching token from {address.to_bech32()}")

    token_computer = TokenComputer()
    identifier = token_computer.extract_identifier_from_extended_identifier(args.identifier)
    nonce = token_computer.extract_nonce_from_extended_identifier(args.identifier)
    token = Token(identifier, nonce)

    response = proxy.get_token_of_account(address, token)

    dump_out_json(response.raw)


def get_transaction(args: Any):
    proxy = _get_proxy(args)
    try:
        response = proxy.get_transaction(args.hash)
    except SDKNetworkProviderError as e:
        raise NetworkProviderError(e.url, e.data)
    except Exception as e:
        raise NetworkProviderError("", str(e))

    dump_out_json(response.raw)


def get_network_config(args: Any):
    proxy = _get_proxy(args)
    config = proxy.get_network_config()

    dump_out_json(config.raw)


def get_network_status(args: Any):
    proxy = _get_proxy(args)
    status = proxy.get_network_status()

    dump_out_json(status.raw)


def _get_address_from_alias_or_config(alias: Optional[str], hrp: str) -> Address:
    if alias:
        account = cli_shared.load_wallet_by_alias(alias=alias, hrp=hrp)
        return account.address
    else:
        account = cli_shared.load_default_wallet(hrp=hrp)
        return account.address


def _get_proxy(args: Any) -> ProxyNetworkProvider:
    if not args.proxy:
        env = MxpyEnv.from_active_env()
        if env.proxy_url:
            logger.info(f"Using proxy URL from config: {env.proxy_url}")
            args.proxy = env.proxy_url
        else:
            raise ArgumentsNotProvidedError("'--proxy' was not provided")

    config = get_config_for_network_providers()
    return ProxyNetworkProvider(url=args.proxy, config=config)
