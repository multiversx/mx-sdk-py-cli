import logging

from erdpy import config

logger = logging.getLogger("cli.config")


def setup_parser(subparsers):
    parser = subparsers.add_parser("config")
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("get", description="Gets a configuration value.")
    sub.add_argument("name")
    sub.set_defaults(func=get_value)

    sub = subparsers.add_parser("set", description="Sets a configuration value.")
    sub.add_argument("name")
    sub.add_argument("value")
    sub.set_defaults(func=set_value)


def get_value(args):
    value = config.get_value(args.name)
    print(value)


def set_value(args):
    config.set_value(args.name, args.value)
