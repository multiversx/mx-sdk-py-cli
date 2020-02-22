import argparse
import logging
import os
import pprint
from argparse import ArgumentParser

from erdpy import config, dependencies, errors, flows, ide, nodedebug, projects
from erdpy._version import __version__

logger = logging.getLogger("cli")


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = setup_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
    else:
        args.func(args)


def setup_parser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    parser.add_argument('-v', '--version', action='version', version=f"erdpy {__version__}")

    install_parser = subparsers.add_parser("install")
    choices = ["C_BUILDCHAIN", "SOL_BUILDCHAIN",
               "RUST_BUILDCHAIN", "NODE_DEBUG"]
    install_parser.add_argument("group", choices=choices)
    install_parser.set_defaults(func=install)

    create_parser = subparsers.add_parser("new")
    create_parser.add_argument("name")
    create_parser.add_argument("--template", required=True)
    create_parser.add_argument("--directory", type=str)
    create_parser.set_defaults(func=create)

    templates_parser = subparsers.add_parser("templates")
    templates_parser.add_argument("--json", action="store_true")
    templates_parser.set_defaults(func=list_templates)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("project", nargs='?', default=os.getcwd())
    build_parser.add_argument("--debug", action="store_true", default=False)
    build_parser.add_argument("--no-optimization", action="store_true", default=False)
    build_parser.set_defaults(func=build)

    deploy_parser = subparsers.add_parser("deploy")
    # TODO: path to project or path to bytecode (hex.arwen).
    deploy_parser.add_argument("project", nargs='?', default=os.getcwd())
    deploy_parser.add_argument("--proxy", required=True)
    deploy_parser.add_argument("--owner", required=True)
    deploy_parser.add_argument("--pem", required=True)
    deploy_parser.add_argument("--arguments", nargs='+')
    deploy_parser.add_argument("--gas-price", default=config.DEFAULT_GASPRICE)
    deploy_parser.add_argument("--gas-limit", default=config.DEFAULT_GASLIMIT)
    deploy_parser.set_defaults(func=deploy)

    call_parser = subparsers.add_parser("call")
    call_parser.add_argument("contract")
    call_parser.add_argument("--proxy", required=True)
    call_parser.add_argument("--caller", required=True)
    call_parser.add_argument("--pem", required=True)
    call_parser.add_argument("--function", required=True)
    call_parser.add_argument("--arguments", nargs='+')
    call_parser.add_argument("--gas-price", default=config.DEFAULT_GASPRICE)
    call_parser.add_argument("--gas-limit", default=config.DEFAULT_GASLIMIT)
    call_parser.set_defaults(func=call)

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("contract")
    query_parser.add_argument("--proxy", required=True)
    query_parser.add_argument("--function", required=True)
    query_parser.add_argument("--arguments", nargs='+')
    query_parser.set_defaults(func=query)

    node_parser = subparsers.add_parser("nodedebug")
    group = node_parser.add_mutually_exclusive_group()
    group.add_argument('--stop', action='store_true')
    group.add_argument('--restart', action='store_true', default=True)
    node_parser.set_defaults(func=do_nodedebug)

    test_parser = subparsers.add_parser("test")
    test_parser.add_argument("project", nargs='?', default=os.getcwd())
    test_parser.add_argument("--wildcard", default="*")
    test_parser.set_defaults(func=run_tests)

    ide_parser = subparsers.add_parser("ide")
    ide_parser.add_argument("workspace", nargs='?', default=os.getcwd())
    ide_parser.set_defaults(func=run_ide)

    return parser


def install(args):
    group = args.group

    try:
        dependencies.install_group(group, overwrite=True)
    except errors.KnownError as err:
        logger.fatal(err)


def list_templates(args):
    json = args.json

    try:
        projects.list_project_templates(json)
    except errors.KnownError as err:
        logger.fatal(err)


def create(args):
    name = args.name
    template = args.template
    directory = args.directory

    try:
        projects.create_from_template(name, template, directory)
    except errors.KnownError as err:
        logger.fatal(err)


def build(args):
    project = args.project
    options = {
        "debug" : args.debug,
        "optimized": not args.no_optimization
    }

    try:
        projects.build_project(project, options)
    except errors.KnownError as err:
        logger.fatal(err)


def deploy(args):
    project = args.project
    owner = args.owner
    pem = args.pem
    proxy = args.proxy
    arguments = args.arguments
    gas_price = args.gas_price
    gas_limit = args.gas_limit

    try:
        flows.deploy_smart_contract(project, owner, pem, proxy, arguments, gas_price, gas_limit)
    except errors.KnownError as err:
        logger.fatal(err)


def call(args):
    contract = args.contract
    caller = args.caller
    pem = args.pem
    proxy = args.proxy
    function = args.function
    arguments = args.arguments
    gas_price = args.gas_price
    gas_limit = args.gas_limit

    try:
        flows.call_smart_contract(contract, caller, pem, proxy, function, arguments, gas_price, gas_limit)
    except errors.KnownError as err:
        logger.fatal(err)


def query(args):
    contract = args.contract
    proxy = args.proxy
    function = args.function
    arguments = args.arguments

    try:
        flows.query_smart_contract(contract, proxy, function, arguments)
    except errors.KnownError as err:
        logger.fatal(err)


def do_nodedebug(args):
    stop = args.stop
    restart = args.restart

    try:
        if restart:
            nodedebug.stop()
            nodedebug.start()
        elif stop:
            nodedebug.stop()
        else:
            nodedebug.start()
    except errors.KnownError as err:
        logger.fatal(err)


def run_tests(args):
    project = args.project
    wildcard = args.wildcard

    try:
        projects.run_tests(project, wildcard)
    except errors.KnownError as err:
        logger.fatal(err)


def run_ide(args):
    workspace = args.workspace
    
    try:
        ide.run_ide(workspace)
    except errors.KnownError as err:
        logger.fatal(err)


if __name__ == "__main__":
    main()
