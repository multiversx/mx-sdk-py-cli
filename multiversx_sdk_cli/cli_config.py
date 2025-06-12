import logging
import os
import sys
from typing import Any

from multiversx_sdk_cli import cli_shared, config, utils
from multiversx_sdk_cli.ux import confirm_continuation

logger = logging.getLogger("cli.config")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "config", "Configure MultiversX CLI (default values etc.)")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "config", "dump", "Dumps the active configuration.")
    sub.add_argument(
        "--defaults",
        required=False,
        help="dump defaults instead of local config",
        action="store_true",
    )
    sub.set_defaults(func=dump)

    sub = cli_shared.add_command_subparser(
        subparsers, "config", "get", "Gets a configuration value from the active configuration."
    )
    _add_name_arg(sub)
    sub.set_defaults(func=get_value)

    sub = cli_shared.add_command_subparser(
        subparsers, "config", "set", "Sets a configuration value for the active configuration."
    )
    _add_name_arg(sub)
    sub.add_argument("value", help="the new value")
    sub.set_defaults(func=set_value)

    sub = cli_shared.add_command_subparser(
        subparsers, "config", "delete", "Deletes a configuration value from the active configuration."
    )
    _add_name_arg(sub)
    sub.set_defaults(func=delete_value)

    sub = cli_shared.add_command_subparser(
        subparsers, "config", "new", "Creates a new configuration and sets it as the active configuration."
    )
    _add_name_arg(sub)
    sub.add_argument(
        "--template",
        required=False,
        help="template from which to create the new config",
    )
    sub.set_defaults(func=new_config)

    sub = cli_shared.add_command_subparser(subparsers, "config", "switch", "Switch to a different config.")
    _add_name_arg(sub)
    sub.set_defaults(func=switch_config)

    sub = cli_shared.add_command_subparser(subparsers, "config", "list", "List available configs")
    sub.set_defaults(func=list_configs)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "config",
        "reset",
        "Deletes the config file. Default config will be used.",
    )
    sub.set_defaults(func=delete_config)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_name_arg(sub: Any):
    sub.add_argument("name", help="the name of the configuration entry")


def dump(args: Any):
    if args.defaults:
        _dump_defaults()
    else:
        _dump_active()


def _dump_defaults():
    utils.dump_out_json(config.get_defaults(), sys.stdout)


def _dump_active():
    utils.dump_out_json(config.get_active(), sys.stdout)


def get_value(args: Any):
    value = config.get_value(args.name)
    print(value)


def set_value(args: Any):
    config.set_value(args.name, args.value)


def delete_value(args: Any):
    config.delete_value(args.name)


def new_config(args: Any):
    config.create_new_config(name=args.name, template=args.template)
    _dump_active()


def switch_config(args: Any):
    config.set_active(args.name)
    _dump_active()


def list_configs(args: Any):
    data = config.read_file()
    configurations = data.get("configurations", {})
    for config_name in configurations.keys():
        if config_name == data.get("active", "default"):
            config_name += "*"
        print(config_name)


def delete_config(args: Any):
    config_file = config.resolve_config_path()
    if not config_file.is_file():
        logger.info("Config file not found. Aborting...")
        return

    confirm_continuation(f"The file `{str(config_file)}` will be deleted. Do you want to continue? (y/n)")
    os.remove(config_file)
    logger.info("Successfully deleted the config file")
