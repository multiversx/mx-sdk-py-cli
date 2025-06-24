import logging
import os
from typing import Any

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.config_wallet import (
    create_new_wallet_config,
    delete_alias,
    delete_config_value,
    get_active_wallet,
    get_value,
    read_wallet_config_file,
    resolve_wallet_config_path,
    set_active,
    set_value,
)
from multiversx_sdk_cli.utils import dump_out_json
from multiversx_sdk_cli.ux import confirm_continuation

logger = logging.getLogger("cli.config_wallet")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers, "config-wallet", "Configure MultiversX CLI to use a default wallet."
    )
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(
        subparsers, "config-wallet", "new", "Creates a new wallet config and sets it as the active wallet."
    )
    sub.add_argument("alias", type=str, help="the alias of the wallet")
    sub.add_argument("--path", type=str, required=False, help="the absolute path to the wallet file")
    sub.add_argument(
        "--template",
        required=False,
        help="a wallet config from which to create the new config",
    )
    sub.set_defaults(func=new_wallet_config)

    sub = cli_shared.add_command_subparser(subparsers, "config-wallet", "list", "List configured wallets")
    sub.set_defaults(func=list_addresses)

    sub = cli_shared.add_command_subparser(subparsers, "config-wallet", "dump", "Dumps the active wallet.")
    sub.set_defaults(func=dump)

    sub = cli_shared.add_command_subparser(
        subparsers, "config-wallet", "get", "Gets a config value from the specified wallet."
    )
    sub.add_argument("value", type=str, help="the value to get from the specified wallet (e.g. path)")
    _add_alias_arg(sub)
    sub.set_defaults(func=get_address_config_value)

    sub = cli_shared.add_command_subparser(
        subparsers, "config-wallet", "set", "Sets a config value for the specified wallet."
    )
    sub.add_argument("key", type=str, help="the key to set for the specified wallet (e.g. index)")
    sub.add_argument("value", type=str, help="the value to set for the specified key")
    _add_alias_arg(sub)
    sub.set_defaults(func=set_address_config_value)

    sub = cli_shared.add_command_subparser(
        subparsers, "config-wallet", "delete", "Deletes a config value from the specified wallet."
    )
    sub.add_argument("value", type=str, help="the value to delete for the specified address")
    _add_alias_arg(sub)
    sub.set_defaults(func=delete_address_config_value)

    sub = cli_shared.add_command_subparser(subparsers, "config-wallet", "switch", "Switch to a different wallet.")
    _add_alias_arg(sub)
    sub.set_defaults(func=switch_address)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "config-wallet",
        "remove",
        "Removes a wallet from the config using the alias. No default wallet will be set. Use `config-wallet switch` to set a new wallet.",
    )
    _add_alias_arg(sub)
    sub.set_defaults(func=remove_address)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "address",
        "reset",
        "Deletes the config file. No default wallet will be set.",
    )
    sub.set_defaults(func=delete_address_config_file)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_alias_arg(sub: Any):
    sub.add_argument("--alias", type=str, required=True, help="the alias of the wallet")


def new_wallet_config(args: Any):
    create_new_wallet_config(name=args.alias, path=args.path, template=args.template)
    dump_out_json(get_active_wallet())


def list_addresses(args: Any):
    _ensure_address_config_file_exists()

    data = read_wallet_config_file()
    dump_out_json(data)


def dump(args: Any):
    _ensure_address_config_file_exists()
    dump_out_json(get_active_wallet())


def get_address_config_value(args: Any):
    _ensure_address_config_file_exists()
    value = get_value(args.value, args.alias)
    print(value)


def set_address_config_value(args: Any):
    _ensure_address_config_file_exists()
    set_value(args.key, args.value, args.alias)


def delete_address_config_value(args: Any):
    _ensure_address_config_file_exists()

    delete_config_value(args.value, args.alias)
    dump_out_json(get_active_wallet())


def switch_address(args: Any):
    _ensure_address_config_file_exists()

    set_active(args.alias)
    dump_out_json(get_active_wallet())


def remove_address(args: Any):
    _ensure_address_config_file_exists()
    delete_alias(args.alias)


def delete_address_config_file(args: Any):
    address_file = resolve_wallet_config_path()
    if not address_file.is_file():
        logger.info("Wallet config file not found. Aborting...")
        return

    confirm_continuation(f"The file `{str(address_file)}` will be deleted. Do you want to continue? (y/n)")
    os.remove(address_file)
    logger.info("Successfully deleted the address config file.")


def _ensure_address_config_file_exists():
    address_file = resolve_wallet_config_path()
    if not address_file.is_file():
        logger.info("Wallet config file not found. Aborting...")
        exit(1)
