import logging
from typing import Any, Optional

from multiversx_sdk import Address, ProxyNetworkProvider, Token, TokenComputer

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.address import (
    get_active_address,
    read_address_config_file,
    resolve_address_config_path,
)
from multiversx_sdk_cli.config import get_config_for_network_providers
from multiversx_sdk_cli.env import MxpyEnv
from multiversx_sdk_cli.errors import (
    AddressConfigFileError,
    ArgumentsNotProvidedError,
    BadUsage,
    NoWalletProvided,
    UnknownAddressAliasError,
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
        subparsers, "get", "keys", "Get the storage (key-value pairs) of an account."
    )
    _add_alias_arg(sub)
    _add_address_arg(sub)
    _add_proxy_arg(sub)
    sub.set_defaults(func=get_keys)

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


def get_keys(args: Any):
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
    response = proxy.get_account_storage_entry(address, args.key)

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
    response = proxy.get_transaction(args.hash)

    dump_out_json(response.raw)


def _get_address_from_alias_or_config(alias: Optional[str], hrp: str) -> Address:
    if alias:
        file_path = resolve_address_config_path()
        if not file_path.is_file():
            raise AddressConfigFileError("The address config file was not found")

        file = read_address_config_file()
        if file == dict():
            raise AddressConfigFileError("Address config file is empty")

        addresses: dict[str, Any] = file["addresses"]
        wallet = addresses.get(alias, None)
        if not wallet:
            raise UnknownAddressAliasError(alias)

        logger.info(f"Using address of [{alias}] from address config.")
        account = cli_shared.load_wallet_from_address_config(wallet=wallet, hrp=hrp)
        return account.address
    else:
        active_address = get_active_address()
        if active_address == dict():
            logger.info("No default wallet found in address config.")
            raise NoWalletProvided()

        alias_of_default_wallet = read_address_config_file().get("active", "")
        logger.info(f"Using address of [{alias_of_default_wallet}] from address config.")

        account = cli_shared.load_wallet_from_address_config(wallet=active_address, hrp=hrp)
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
