import logging
from typing import Any

from erdpy import cli_shared, testnet

logger = logging.getLogger("cli.testnet")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers,
        "testnet",
        "Set up, start and control local testnets"
    )
    subparsers = parser.add_subparsers()

    help_config_file = "An optional configuration file describing the testnet"

    # Prerequisites
    sub = cli_shared.add_command_subparser(
        subparsers,
        "testnet",
        "prerequisites",
        "Download and verify the prerequisites for running a testnet"
    )
    sub.add_argument("--configfile", type=str, required=False, default=None,
                     help=help_config_file)
    sub.set_defaults(func=testnet_prerequisites)

    # Start
    sub = cli_shared.add_command_subparser(
        subparsers,
        "testnet",
        "start",
        "Start a testnet"
    )
    sub.add_argument("--configfile", type=str, required=False, default=None,
                     help=help_config_file)
    sub.set_defaults(func=testnet_start)

    # Config
    sub = cli_shared.add_command_subparser(
        subparsers,
        "testnet",
        "config",
        "Configure a testnet (required before starting it the first time or after clean)"
    )
    sub.add_argument("--configfile", type=str, required=False, default=None,
                     help=help_config_file)
    sub.set_defaults(func=testnet_config)

    # Clean
    sub = cli_shared.add_command_subparser(
        subparsers,
        "testnet",
        "clean",
        "Erase the currently configured testnet (must be already stopped)"
    )
    sub.add_argument("--configfile", type=str, required=False, default=None,
                     help=help_config_file)
    sub.set_defaults(func=testnet_clean)


def testnet_start(args):
    logger.info("Starting testnet...")
    testnet.start(args)


def testnet_config(args):
    logger.info("Configuring testnet...")
    testnet.configure(args)


def testnet_clean(args):
    logger.info("Cleaning testnet...")
    testnet.clean(args)


def testnet_prerequisites(args):
    logger.info("Preparing prerequisites...")
    testnet.install_dependencies()
