import logging
import os
from typing import Any

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.address import (
    create_new_address_config,
    delete_alias,
    delete_config_value,
    get_active_address,
    get_value,
    read_address_config_file,
    resolve_address_config_path,
    set_active,
    set_value,
)
from multiversx_sdk_cli.utils import dump_out_json
from multiversx_sdk_cli.ux import confirm_continuation

logger = logging.getLogger("cli.address")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "address", "Configure MultiversX CLI to use a default wallet.")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(
        subparsers, "address", "new", "Creates a new address config and sets it as the active address."
    )
    _add_alias_arg(sub)
    sub.add_argument(
        "--template",
        required=False,
        help="an address config from which to create the new address",
    )
    sub.set_defaults(func=new_address_config)

    sub = cli_shared.add_command_subparser(subparsers, "address", "list", "List available addresses")
    sub.set_defaults(func=list_addresses)

    sub = cli_shared.add_command_subparser(subparsers, "address", "dump", "Dumps the active address.")
    sub.set_defaults(func=dump)

    sub = cli_shared.add_command_subparser(subparsers, "address", "get", "Gets a config value from the active address.")
    sub.add_argument("value", type=str, help="the value to get from the active address (e.g. path)")
    sub.set_defaults(func=get_address_config_value)

    sub = cli_shared.add_command_subparser(subparsers, "address", "set", "Sets a config value for the active address.")
    sub.add_argument("key", type=str, help="the key to set for the active address (e.g. index)")
    sub.add_argument("value", type=str, help="the value to set for the specified key")
    sub.set_defaults(func=set_address_config_value)

    sub = cli_shared.add_command_subparser(
        subparsers, "address", "delete", "Deletes a config value from the active address."
    )
    sub.add_argument("value", type=str, help="the value to delete for the active address")
    sub.set_defaults(func=delete_address_config_value)

    sub = cli_shared.add_command_subparser(subparsers, "address", "switch", "Switch to a different address.")
    _add_alias_arg(sub)
    sub.set_defaults(func=switch_address)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "address",
        "remove",
        "Deletes an address using the alias. No default address will be set. Use `address switch` to set a new address.",
    )
    _add_alias_arg(sub)
    sub.set_defaults(func=remove_address)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "address",
        "reset",
        "Deletes the config file. No default address will be set.",
    )
    sub.set_defaults(func=delete_address_config_file)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_alias_arg(sub: Any):
    sub.add_argument("alias", type=str, help="the alias of the wallet")


def new_address_config(args: Any):
    create_new_address_config(name=args.alias, template=args.template)
    dump_out_json(get_active_address())


def list_addresses(args: Any):
    _ensure_address_config_file_exists()

    data = read_address_config_file()
    dump_out_json(data)


def dump(args: Any):
    _ensure_address_config_file_exists()
    dump_out_json(get_active_address())


def get_address_config_value(args: Any):
    _ensure_address_config_file_exists()
    value = get_value(args.value)
    print(value)


def set_address_config_value(args: Any):
    _ensure_address_config_file_exists()
    set_value(args.key, args.value)


def delete_address_config_value(args: Any):
    _ensure_address_config_file_exists()

    delete_config_value(args.value)
    dump_out_json(get_active_address())


def switch_address(args: Any):
    _ensure_address_config_file_exists()

    set_active(args.alias)
    dump_out_json(get_active_address())


def remove_address(args: Any):
    _ensure_address_config_file_exists()
    delete_alias(args.alias)


def delete_address_config_file(args: Any):
    address_file = resolve_address_config_path()
    if not address_file.is_file():
        logger.info("Address config file not found. Aborting...")
        return

    confirm_continuation(f"The file `{str(address_file)}` will be deleted. Do you want to continue? (y/n)")
    os.remove(address_file)
    logger.info("Successfully deleted the address config file.")


def _ensure_address_config_file_exists():
    address_file = resolve_address_config_path()
    if not address_file.is_file():
        logger.info("Address config file not found. Aborting...")
        exit(1)
