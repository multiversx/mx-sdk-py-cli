import logging
from typing import Any

from multiversx_sdk_cli import cli_shared, config, dependencies, errors
from multiversx_sdk_cli.dependencies.install import get_deps_dict
from multiversx_sdk_cli.dependencies.modules import DependencyModule

logger = logging.getLogger("cli.deps")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "deps", "Manage dependencies or multiversx-sdk modules")
    subparsers = parser.add_subparsers()

    choices = ['all'] + list(get_deps_dict().keys())

    sub = cli_shared.add_command_subparser(subparsers, "deps", "install", "Install dependencies or multiversx-sdk modules.")
    sub.add_argument("name", choices=choices, help="the dependency to install")
    sub.add_argument("--overwrite", action="store_true", default=False, help="whether to overwrite an existing installation")
    sub.set_defaults(func=install)

    sub = cli_shared.add_command_subparser(subparsers, "deps", "check", "Check whether a dependency is installed.")
    sub.add_argument("name", choices=choices, help="the dependency to check")
    sub.set_defaults(func=check)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def install(args: Any):
    name: str = args.name
    overwrite: bool = args.overwrite
    dependencies.install_module(name, overwrite)


def check(args: Any):
    name: str = args.name
    if name == "all":
        all_dependencies = dependencies.get_all_deps()

        for dependency in all_dependencies:
            check_module_is_installed(dependency)
    else:
        module = dependencies.get_module_by_key(name)
        check_module_is_installed(module)


def check_module_is_installed(module: DependencyModule) -> None:
    tag_to_check: str = config.get_dependency_tag(module.key)
    resolution: str = config.get_dependency_resolution(module.key)
    resolution = resolution if resolution else "HOST"

    logger.info(f"Checking dependency: module = {module.key}, tag = {tag_to_check}, resolution = {resolution}")

    installed = module.is_installed(tag_to_check)
    if installed:
        logger.info(f"[{module.key} {tag_to_check}] is installed.")
        return

    raise errors.DependencyMissing(module.key, tag_to_check)
