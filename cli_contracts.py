import argparse
import os
from typing import Any

from erdpy import cli_shared, facade, projects


def setup_parser(subparsers: Any) -> Any:
    parser = subparsers.add_parser(
        "contract",
        usage="erdpy contract COMMAND [-h] options",
        description="Build, deploy and interact with Smart Contracts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser._positionals.title = "COMMANDS"

    subparsers = parser.add_subparsers()

    sub = _add_command_subparser(subparsers, "new", "Create a new Smart Contract project based on a template.")
    sub.add_argument("name")
    sub.add_argument("--template", required=True, help="the template to use")
    sub.add_argument("--directory", type=str, default=os.getcwd(), help="🗀 the parent directory of the project (default: current directory)")
    sub.set_defaults(func=create)

    sub = _add_command_subparser(subparsers, "templates", "List the available Smart Contract templates.")
    sub.set_defaults(func=list_templates)

    sub = _add_command_subparser(subparsers, "build", "Build a Smart Contract project using the appropriate buildchain.")
    _add_project_arg(sub)
    sub.add_argument("--debug", action="store_true", default=False, help="set debug flag (default: %(default)s)")
    sub.add_argument("--no-optimization", action="store_true", default=False, help="bypass optimizations (for clang) (default: %(default)s)")
    sub.set_defaults(func=build)

    sub = subparsers.add_parser("clean", description="Clean a Smart Contract project.")
    _add_project_arg(sub)
    sub.set_defaults(func=clean)

    sub = _add_command_subparser(subparsers, "deploy", "Deploy a Smart Contract.")
    _add_project_arg(sub)
    _add_metadata_arg(sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_wallet_args(sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(sub)
    _add_arguments_arg(sub)

    sub.set_defaults(func=deploy)

    sub = _add_command_subparser(subparsers, "call", "Interact with a Smart Contract (execute function).")
    _add_contract_arg(sub)
    cli_shared.add_wallet_args(sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(sub)
    _add_function_arg(sub)
    _add_arguments_arg(sub)

    sub.set_defaults(func=call)

    sub = _add_command_subparser(subparsers, "upgrade", "Upgrade a previously-deployed Smart Contract")
    _add_contract_arg(sub)
    _add_project_arg(sub)
    _add_metadata_arg(sub)
    cli_shared.add_wallet_args(sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(sub)
    _add_arguments_arg(sub)

    sub.set_defaults(func=upgrade)

    sub = _add_command_subparser(subparsers, "query", "Query a Smart Contract (call a pure function)")
    _add_contract_arg(sub)
    cli_shared.add_proxy_arg(sub)
    _add_function_arg(sub)
    _add_arguments_arg(sub)
    sub.set_defaults(func=query)

    parser.epilog = """
----------------
COMMANDS summary
----------------
"""
    for choice, sub in subparsers.choices.items():
        parser.epilog += (f"{choice.ljust(30)} {sub.description}\n")

    return subparsers


def _add_command_subparser(subparsers: Any, command: str, description: str):
    return subparsers.add_parser(
        command,
        usage=f"erdpy contract {command} [-h] ...",
        description=description,
        formatter_class=cli_shared.wider_help_formatter
    )


def _add_project_arg(sub: Any):
    sub.add_argument("project", nargs='?', default=os.getcwd(), help="🗀 the project directory (default: current directory)")


def _add_contract_arg(sub: Any):
    sub.add_argument("contract", help="🖄 the address of the Smart Contract")


def _add_function_arg(sub: Any):
    sub.add_argument("--function", required=True, help="the function to call")


def _add_arguments_arg(sub: Any):
    sub.add_argument("--arguments", nargs='+', help="arguments for the contract transaction, as numbers or hex-encoded. E.g. --arguments 42 0x64 1000 0xabba")


def _add_metadata_arg(sub: Any):
    sub.add_argument("--metadata-upgradeable", action="store_true", default=False, help="⚙ whether the contract is upgradeable (default: %(default)s)")


def list_templates(args: Any):
    projects.list_project_templates()


def create(args: Any):
    name = args.name
    template = args.template
    directory = args.directory

    projects.create_from_template(name, template, directory)


def clean(args: Any):
    project = args.project
    projects.clean_project(project)


def build(args: Any):
    project = args.project
    options = {
        "debug": args.debug,
        "optimized": not args.no_optimization,
        "verbose": args.verbose
    }

    projects.build_project(project, options)


def deploy(args: Any):
    facade.deploy_smart_contract(args)


def call(args: Any):
    facade.call_smart_contract(args)


def upgrade(args: Any):
    facade.upgrade_smart_contract(args)


def query(args: Any):
    facade.query_smart_contract(args)
