import logging

from erdpy import dependencies, errors

logger = logging.getLogger("cli.deps")


def setup_parser(subparsers):
    parser = subparsers.add_parser("deps")
    subparsers = parser.add_subparsers()

    choices = ["clang", "cpp", "rust", "arwentools"]

    sub = subparsers.add_parser("install", description="Install dependencies or elrond-sdk packages.")
    sub.add_argument("group", choices=choices, help="the dependency to install")
    sub.add_argument("--overwrite", action="store_true", default=False)
    sub.set_defaults(func=install)

    sub = subparsers.add_parser("check", description="Check whether a dependency is installed.")
    sub.add_argument("group", choices=choices, help="the dependency to check")
    sub.set_defaults(func=check)


def install(args):
    group = args.group
    overwrite = args.overwrite
    dependencies.install_group(group, overwrite=overwrite)


def check(args):
    group = args.group
    installed = dependencies.is_installed(group)
    if installed:
        logger.info(f"[{group}] is installed.")
        return
    raise errors.DependencyMissing(group)
