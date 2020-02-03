import logging
import pprint
from argparse import ArgumentParser

from erdpy import dependencies, projects, errors

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
    choices = ["C", "soll", "rust", "nodedebug"]
    install_parser.add_argument("module", choices=choices)
    install_parser.set_defaults(func=install)

    create_parser = subparsers.add_parser("new")
    create_parser.add_argument("name")
    create_parser.add_argument("--template", required=True)
    create_parser.add_argument("--directory", type=str)
    create_parser.set_defaults(func=create)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("project")
    build_parser.add_argument("--debug", action="store_true")
    build_parser.set_defaults(func=build)

    return parser


def install(args):
    module = args.module

    try:
        dependencies.install(module)
    except errors.KnownError as err:
        logger.fatal(err)


def create(args):
    name = args.name
    template = args.template
    directory = args.directory

    try:
        projects.create_project(name, template, directory)
    except errors.KnownError as err:
        logger.fatal(err)


def build(args):
    logger.info("build")
    pprint.pprint(args)


if __name__ == "__main__":
    main()
