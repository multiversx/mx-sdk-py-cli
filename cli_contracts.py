import os
import sys
from argparse import FileType

from erdpy import config, facade, ide, projects
from erdpy.utils import is_arg_present


def setup_parser(subparsers):
    parser = subparsers.add_parser("contract")
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("new", description="Create a new Smart Contract project based on a template.")
    sub.add_argument("name")
    sub.add_argument("--template", required=True, help="the template to use")
    sub.add_argument("--directory", type=str, default=os.getcwd(), help="the parent directory of the project")
    sub.set_defaults(func=create)

    sub = subparsers.add_parser("templates", description="List the available Smart Contract templates.")
    sub.set_defaults(func=list_templates)

    sub = subparsers.add_parser("build", description="Build a Smart Contract project using the appropriate buildchain.")
    sub.add_argument("project", nargs='?', default=os.getcwd())
    sub.add_argument("--debug", action="store_true", default=False)
    sub.add_argument("--no-optimization", action="store_true", default=False)
    sub.set_defaults(func=build)

    sub = subparsers.add_parser("clean", description="Clean a Smart Contract project.")
    sub.add_argument("project", nargs='?', default=os.getcwd())
    sub.set_defaults(func=clean)

    sub = subparsers.add_parser("deploy", description="Deploy a Smart Contract.")
    sub.add_argument("project", nargs='?', default=os.getcwd(), help="the project directory")
    sub.add_argument("--nonce", type=int, required=not("--recall-nonce" in sys.argv))
    sub.add_argument("--recall-nonce", action="store_true", default=False)
    sub.add_argument("--proxy", required=True, help="the URL of the proxy")
    sub.add_argument("--pem", required=not (is_arg_present("--keyfile", sys.argv)), help="the PEM file of the owner")
    sub.add_argument("--keyfile", required=not (is_arg_present("--pem", sys.argv)))
    sub.add_argument("--passfile", required=not (is_arg_present("--pem", sys.argv)))
    sub.add_argument("--arguments", nargs='+', help="constructor arguments")
    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE, help="the gas price")
    sub.add_argument("--gas-limit", required=True, help="the gas limit")
    sub.add_argument("--value", default="0", help="the value to transfer")
    sub.add_argument("--metadata-upgradeable", action="store_true", default=False, help="whether the contract is "
                                                                                        "upgradeable")
    sub.add_argument("--outfile", type=FileType("w"), default=sys.stdout, help="where to save the command's output")
    sub.add_argument("--chain", default=config.get_chain_id())
    sub.add_argument("--version", type=int, default=config.get_tx_version())
    sub.set_defaults(func=deploy)

    sub = subparsers.add_parser("call")
    sub.add_argument("contract")
    sub.add_argument("--nonce", type=int, required=not("--recall-nonce" in sys.argv))
    sub.add_argument("--recall-nonce", action="store_true", default=False)
    sub.add_argument("--proxy", required=True)

    sub.add_argument("--pem", required=not (is_arg_present("--keyfile", sys.argv)), help="the PEM file")
    sub.add_argument("--keyfile", required=not (is_arg_present("--pem", sys.argv)))
    sub.add_argument("--passfile", required=not (is_arg_present("--pem", sys.argv)))

    sub.add_argument("--function", required=True)
    sub.add_argument("--arguments", nargs='+')
    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    sub.add_argument("--gas-limit", required=True)
    sub.add_argument("--value", default="0")
    sub.add_argument("--chain", default=config.get_chain_id())
    sub.add_argument("--version", type=int, default=config.get_tx_version())
    sub.set_defaults(func=call)

    sub = subparsers.add_parser("upgrade")
    sub.add_argument("contract")
    sub.add_argument("project")
    sub.add_argument("--nonce", type=int, required=not("--recall-nonce" in sys.argv))
    sub.add_argument("--recall-nonce", action="store_true", default=False)
    sub.add_argument("--proxy", required=True)

    sub.add_argument("--pem", required=not (is_arg_present("--keyfile", sys.argv)), help="the PEM file of the owner")
    sub.add_argument("--keyfile", required=not (is_arg_present("--pem", sys.argv)))
    sub.add_argument("--passfile", required=not (is_arg_present("--pem", sys.argv)))

    sub.add_argument("--arguments", nargs='+')
    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    sub.add_argument("--gas-limit", required=True)
    sub.add_argument("--value", default="0")
    sub.add_argument("--metadata-upgradeable", action="store_true", default=False)
    sub.add_argument("--chain", default=config.get_chain_id())
    sub.add_argument("--version", type=int, default=config.get_tx_version())
    sub.set_defaults(func=upgrade)

    sub = subparsers.add_parser("query")
    sub.add_argument("contract")
    sub.add_argument("--proxy", required=True)
    sub.add_argument("--function", required=True)
    sub.add_argument("--arguments", nargs='+')
    sub.set_defaults(func=query)

    sub = subparsers.add_parser("ide")
    sub.add_argument("workspace", nargs='?', default=os.getcwd())
    sub.set_defaults(func=run_ide)


def list_templates(args):
    projects.list_project_templates()


def create(args):
    name = args.name
    template = args.template
    directory = args.directory

    projects.create_from_template(name, template, directory)


def clean(args):
    project = args.project
    projects.clean_project(project)


def build(args):
    project = args.project
    options = {
        "debug": args.debug,
        "optimized": not args.no_optimization,
        "verbose": args.verbose
    }

    projects.build_project(project, options)


def deploy(args):
    facade.deploy_smart_contract(args)


def call(args):
    facade.call_smart_contract(args)


def upgrade(args):
    facade.upgrade_smart_contract(args)


def query(args):
    facade.query_smart_contract(args)


def run_ide(args):
    workspace = args.workspace
    ide.run_ide(workspace)


# def do_nodedebug(args):
#     stop = args.stop
#     restart = args.restart

#     if restart:
#         nodedebug.stop()
#         nodedebug.start()
#     elif stop:
#         nodedebug.stop()
#     else:
#         nodedebug.start()
