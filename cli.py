import argparse
import logging
import pprint
from argparse import ArgumentParser

from erdpy import dependencies, errors, flows, nodedebug, projects

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
    deploy_parser.add_argument("--proxy", required=True)
    deploy_parser.add_argument("--address", required=True)
    deploy_parser.add_argument("--pem", required=True)
    deploy_parser.add_argument("--params", type=argparse.FileType('r'))
    deploy_parser.add_argument("--gas-price", default=200000000000000)
    deploy_parser.add_argument("--gas-limit", default=500000000)
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
        projects.list_project_templates()
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
    debug = args.debug

    try:
        projects.build_project(project, debug)
    except errors.KnownError as err:
        logger.fatal(err)


def deploy(args):
    project = args.project
    address = args.address
    pem = args.pem
    proxy = args.proxy
    #params = args.params

    try:
        flows.deploy_smart_contract(project, address, pem, proxy)
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
