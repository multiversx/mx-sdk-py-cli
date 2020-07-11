import argparse
import os
import sys
from argparse import FileType
from typing import Any, Text

from erdpy import config, facade, projects
from erdpy.utils import is_arg_present


def setup_parser(subparsers: Any) -> Any:
    parser = subparsers.add_parser(
        "contract",
        usage="erdpy contract COMMAND [-h] options",
        description="Build, deploy and interact with Smart Contracts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser._positionals.title = "COMMANDS"

    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("new", description="Create a new Smart Contract project based on a template.")
    sub.add_argument("name")
    sub.add_argument("--template", required=True, help="the template to use")
    sub.add_argument("--directory", type=str, default=os.getcwd(), help="the parent directory of the project")
    sub.set_defaults(func=create)

    sub = subparsers.add_parser("templates", description="List the available Smart Contract templates.")
    sub.set_defaults(func=list_templates)

    sub = subparsers.add_parser("build", description="Build a Smart Contract project using the appropriate buildchain.")
    sub.add_argument("project", nargs='?', default=os.getcwd(), help="the project directory")
    sub.add_argument("--debug", action="store_true", default=False, help="set debug flag")
    sub.add_argument("--no-optimization", action="store_true", default=False, help="bypass optimizations (for clang)")
    sub.set_defaults(func=build)

    sub = subparsers.add_parser("clean", description="Clean a Smart Contract project.")
    sub.add_argument("project", nargs='?', default=os.getcwd())
    sub.set_defaults(func=clean)

    sub = subparsers.add_parser(
        "deploy",
        usage="erdpy contract deploy [-h] options",
        description="Deploy a Smart Contract.",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=40)
    )
    sub.add_argument("project", nargs='?', default=os.getcwd(), help="the project directory")
    _add_common_arguments(sub)
    sub.add_argument("--metadata-upgradeable", action="store_true", default=False, help="whether the contract is upgradeable")
    sub.add_argument("--outfile", type=FileType("w"), default=sys.stdout, help="where to save the command's output")
    sub.set_defaults(func=deploy)

    sub = subparsers.add_parser("call", description="Interact with a Smart Contract (execute function)")
    sub.add_argument("contract")
    _add_common_arguments(sub)
    sub.set_defaults(func=call)

    sub = subparsers.add_parser("upgrade", description="Upgrade a previously-deployed Smart Contract")
    sub.add_argument("contract")
    sub.add_argument("project")
    _add_common_arguments(sub)
    sub.add_argument("--metadata-upgradeable", action="store_true", default=False)
    sub.set_defaults(func=upgrade)

    sub = subparsers.add_parser("query", description="Query a Smart Contract (call a pure function)")
    sub.add_argument("contract")
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--function", required=True)
    sub.add_argument("--arguments", nargs='+')
    sub.set_defaults(func=query)

    # sub = subparsers.add_parser("ide")
    # sub.add_argument("workspace", nargs='?', default=os.getcwd())
    # sub.set_defaults(func=run_ide)

    parser.epilog = """
----------------
COMMANDS summary
----------------
"""
    for choice, sub in subparsers.choices.items():
        parser.epilog += (f"{choice.ljust(30)} {sub.description}\n")

    return subparsers


def _add_common_arguments(sub: Any):
    sub.add_argument("--nonce", type=int, required=not("--recall-nonce" in sys.argv), help="the nonce for the transaction")
    sub.add_argument("--recall-nonce", action="store_true", default=False, help="whether to recall the nonce when creating the transaction")
    sub.add_argument("--proxy", default=config.get_proxy(), help="the URL of the proxy")
    sub.add_argument("--pem", required=not (is_arg_present("--keyfile", sys.argv)), help="the PEM file")
    sub.add_argument("--keyfile", required=not (is_arg_present("--pem", sys.argv)), help="a JSON keyfile")
    sub.add_argument("--passfile", required=not (is_arg_present("--pem", sys.argv)), help="a file containing keyfile's password")
    sub.add_argument("--arguments", nargs='+', help="arguments for the contract transaction")
    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE, help="the gas price")
    sub.add_argument("--gas-limit", required=True, help="the gas limit")
    sub.add_argument("--value", default="0", help="the value to transfer")
    sub.add_argument("--chain", default=config.get_chain_id(), help="the chain identifier")
    sub.add_argument("--version", type=int, default=config.get_tx_version(), help="the transaction version")


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


# def run_ide(args: Any):
#     workspace = args.workspace
#     ide.run_ide(workspace)
