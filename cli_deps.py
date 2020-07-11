import logging
from typing import Any

from erdpy import config, dependencies, errors

logger = logging.getLogger("cli.deps")


def setup_parser(subparsers: Any) -> Any:
    parser = subparsers.add_parser("deps", description="Manage dependencies or elrond-sdk modules")
    subparsers = parser.add_subparsers()

    choices = ["clang", "cpp", "rust", "arwentools"]

    sub = subparsers.add_parser("install", description="Install dependencies or elrond-sdk modules.")
    sub.add_argument("name", choices=choices, help="the dependency to install")
    sub.add_argument("--overwrite", action="store_true", default=False, help="whether to overwrite an existing installation")
    sub.add_argument("--tag", help="the tag or version to install")
    sub.set_defaults(func=install)

    sub = subparsers.add_parser("check", description="Check whether a dependency is installed.")
    sub.add_argument("name", choices=choices, help="the dependency to check")
    sub.add_argument("--tag", help="the tag or version to check")
    sub.set_defaults(func=check)

    return subparsers


def install(args: Any):
    name: str = args.name
    tag: str = args.tag
    overwrite: bool = args.overwrite
    dependencies.install_module(name, tag, overwrite)


def check(args: Any):
    name: str = args.name
    tag: str = args.tag
    module = dependencies.get_module_by_key(name)
    default_tag: str = config.get_dependency_tag(module.key)
    tag_to_check = tag or default_tag
    installed = module.is_installed(tag_to_check)
    if installed:
        print(f"[{name} {tag_to_check}] is installed. Default version (tag) is [{default_tag}].")
        return

    raise errors.DependencyMissing(name, tag_to_check)
