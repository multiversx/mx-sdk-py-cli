from erdpy import cli_shared
import logging
import sys
from typing import Any

from erdpy import config, utils

logger = logging.getLogger("cli.config")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "config", "Configure elrond-sdk (default values etc.)")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "config", "dump", "Dumps configuration.")
    sub.set_defaults(func=dump)

    sub = cli_shared.add_command_subparser(subparsers, "config", "get", "Gets a configuration value.")
    _add_name_arg(sub)
    sub.set_defaults(func=get_value)

    sub = cli_shared.add_command_subparser(subparsers, "config", "set", "Sets a configuration value.")
    _add_name_arg(sub)
    sub.add_argument("value", help="the new value")
    sub.set_defaults(func=set_value)

    sub = cli_shared.add_command_subparser(subparsers, "config", "new", "Creates a new configuration.")
    _add_name_arg(sub)
    sub.add_argument("template", help="template from which to create the new config")
    sub.set_defaults(func=new_config)

    sub = cli_shared.add_command_subparser(subparsers, "config", "switch", "Switch to a new defined config")
    _add_name_arg(sub)
    sub.set_defaults(func=switch_config)

    sub = cli_shared.add_command_subparser(subparsers, "config", "list", "List available configs")
    sub.set_defaults(func=list_configs)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_name_arg(sub: Any):
    sub.add_argument("name", help="the name of the configuration entry")


def dump(args: Any):
    data = config.get_active()
    utils.dump_out_json(data, sys.stdout)


def get_value(args: Any):
    value = config.get_value(args.name)
    print(value)


def set_value(args: Any):
    config.set_value(args.name, args.value)


def new_config(args: Any):
    config.create_new(args.name, args.template)
    dump()


def switch_config(args: Any):
    config.set_active(args.name)
    dump()

def list_configs(args: Any):
    data = config.read_file()
    configs = {}

    for
