from erdpy import dependencies


def setup_parser_install(subparsers):
    sub = subparsers.add_parser("install", description="Install dependencies or elrond-sdk packages.")
    choices = ["clang", "rust", "arwentools"]
    sub.add_argument("group", choices=choices, help="the package to install")
    sub.add_argument("--overwrite", action="store_true", default=False)
    sub.set_defaults(func=install)


def install(args):
    group = args.group
    overwrite = args.overwrite
    dependencies.install_group(group, overwrite=overwrite)
