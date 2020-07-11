import logging
import sys
from typing import Any

from erdpy import config, utils

logger = logging.getLogger("cli.config")


def setup_parser(subparsers: Any):
    parser = subparsers.add_parser("config")
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("dump", description="Dumps configuration.")
    sub.set_defaults(func=dump)

    sub = subparsers.add_parser("get", description="Gets a configuration value.")
    sub.add_argument("name")
    sub.set_defaults(func=get_value)

    sub = subparsers.add_parser("set", description="Sets a configuration value.")
    sub.add_argument("name")
    sub.add_argument("value")
    sub.set_defaults(func=set_value)


def dump(args: Any):
    data = config.read_file()
    utils.dump_out_json(data, sys.stdout)


def get_value(args: Any):
    value = config.get_value(args.name)
    print(value)


def set_value(args: Any):
    config.set_value(args.name, args.value)
