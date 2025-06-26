import logging
import os
from typing import Any

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.config_env import (
    create_new_env,
    delete_env,
    delete_value,
    get_active_env,
    get_defaults,
    get_value,
    read_env_file,
    resolve_env_path,
    set_active,
    set_value,
)
from multiversx_sdk_cli.utils import dump_out_json
from multiversx_sdk_cli.ux import confirm_continuation

logger = logging.getLogger("cli.config_env")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers, "config-env", "Configure MultiversX CLI to use specific environment values."
    )
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(
        subparsers, "config-env", "new", "Creates a new environment and sets it as the active environment."
    )
    sub.add_argument("name", type=str, help="the name of the new environment")
    sub.add_argument(
        "--template",
        required=False,
        help="an environment from which to create the new environment",
    )
    sub.set_defaults(func=new_env)

    sub = cli_shared.add_command_subparser(
        subparsers, "config-env", "get", "Gets an env value from the specified environment."
    )
    _add_name_arg(sub)
    _add_env_arg(sub)
    sub.set_defaults(func=get_env_value)

    sub = cli_shared.add_command_subparser(
        subparsers, "config-env", "set", "Sets an env value for the specified environment."
    )
    _add_name_arg(sub)
    sub.add_argument("value", type=str, help="the new value")
    _add_env_arg(sub)
    sub.set_defaults(func=set_env_value)

    sub = cli_shared.add_command_subparser(subparsers, "config-env", "dump", "Dumps the active environment.")
    sub.add_argument(
        "--default",
        required=False,
        help="dumps the default environment instead of the active one.",
        action="store_true",
    )
    sub.set_defaults(func=dump)

    sub = cli_shared.add_command_subparser(
        subparsers, "config-env", "delete", "Deletes an env value from the specified environment."
    )
    _add_name_arg(sub)
    _add_env_arg(sub)
    sub.set_defaults(func=delete_env_value)

    sub = cli_shared.add_command_subparser(subparsers, "config-env", "switch", "Switch to a different environment.")
    _add_env_arg(sub)
    sub.set_defaults(func=switch_env)

    sub = cli_shared.add_command_subparser(subparsers, "config-env", "list", "List available environments")
    sub.set_defaults(func=list_envs)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "config-env",
        "remove",
        "Deletes an environment from the env file. Use `mxpy config-env switch` to switch to another env.",
    )
    _add_env_arg(sub)
    sub.set_defaults(func=remove_env_entry)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "config-env",
        "reset",
        "Deletes the environment file. Default env will be used.",
    )
    sub.set_defaults(func=delete_env_file)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_name_arg(sub: Any):
    sub.add_argument("name", type=str, help="the name of the configuration entry")


def _add_env_arg(sub: Any):
    sub.add_argument("--env", required=True, type=str, help="the name of the environment to operate on")


def dump(args: Any):
    if args.default:
        dump_out_json(get_defaults())
    else:
        dump_out_json(get_active_env())


def get_env_value(args: Any):
    value = get_value(args.name, args.env)
    print(value)


def set_env_value(args: Any):
    set_value(args.name, args.value, args.env)


def delete_env_value(args: Any):
    delete_value(args.name, args.env)


def new_env(args: Any):
    create_new_env(name=args.name, template=args.template)
    dump_out_json(get_active_env())


def switch_env(args: Any):
    set_active(args.env)
    dump_out_json(get_active_env())


def list_envs(args: Any):
    data = read_env_file()
    dump_out_json(data)


def remove_env_entry(args: Any):
    envs_file = resolve_env_path()
    if not envs_file.is_file():
        logger.info("Environment file not found. Aborting...")
        return

    delete_env(args.env)


def delete_env_file(args: Any):
    envs_file = resolve_env_path()
    if not envs_file.is_file():
        logger.info("Environment file not found. Aborting...")
        return

    confirm_continuation(f"The file `{str(envs_file)}` will be deleted. Do you want to continue? (y/n)")
    os.remove(envs_file)
    logger.info("Successfully deleted the environment file.")
