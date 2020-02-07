import logging
import pprint
import argparse
from argparse import ArgumentParser

from erdpy import building, dependencies, errors, templates, nodedebug

logger = logging.getLogger("cli")


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = setup_parser()
    args = parser.parse_args()

    # TODO: raise parser error if deploy --testnet no --pem etc.
    # https://stackoverflow.com/a/19414853/1475331

    if not hasattr(args, "func"):
        parser.print_help()
    else:
        args.func(args)


def setup_parser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

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
    templates_parser.set_defaults(func=list_templates)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("project")
    build_parser.add_argument("--debug", action="store_true")
    build_parser.set_defaults(func=build)

    deploy_parser = subparsers.add_parser("deploy")
    deploy_parser.add_argument("project")
    group = deploy_parser.add_mutually_exclusive_group()
    group.add_argument('--debug', action='store_true')
    group.add_argument('--testnet', action='store_true')
    deploy_parser.add_argument("--proxy")
    deploy_parser.add_argument("--pem", type=argparse.FileType('r'))
    deploy_parser.add_argument("--params", type=argparse.FileType('r'))
    # TODO gasLimit, good default
    # TODO gasPrice, good default
    deploy_parser.set_defaults(func=deploy)

    node_parser = subparsers.add_parser("nodedebug")
    group = node_parser.add_mutually_exclusive_group()
    group.add_argument('--stop', action='store_true')
    group.add_argument('--restart', action='store_true')
    node_parser.set_defaults(func=do_nodedebug)

    return parser


def install(args):
    group = args.group

    try:
        dependencies.install_group(group, overwrite=True)
    except errors.KnownError as err:
        logger.fatal(err)


def list_templates(args):
    try:
        templates.list_templates()
    except errors.KnownError as err:
        logger.fatal(err)


def create(args):
    name = args.name
    template = args.template
    directory = args.directory

    try:
        templates.create_project(name, template, directory)
    except errors.KnownError as err:
        logger.fatal(err)


def build(args):
    project = args.project
    debug = args.debug

    try:
        building.build_project(project, debug)
    except errors.KnownError as err:
        logger.fatal(err)


def deploy(args):
    try:
        pass
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

if __name__ == "__main__":
    main()

    # TODO
    # contract = SmartContract()
    # gateway = NodeDebug() / Testnet("..."). Gateway interface.
    # 
    # tx_hash, contract_address = gateway.deploy(contract)
    # contract.set_address(contract_address)
    # contract.execute("increment", 1)
