import logging
from typing import Any, List

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.testnet import (step_build_software, step_clean,
                                        step_config, step_prerequisites,
                                        step_start)

logger = logging.getLogger("cli.testnet")


def setup_parser(args: List[str], subparsers: Any) -> Any:
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
    sub.add_argument("--configfile", type=str, required=False, default=None, help=help_config_file)
    sub.set_defaults(func=testnet_prerequisites)

    # Build
    sub = cli_shared.add_command_subparser(
        subparsers,
        "testnet",
        "build",
        "Build necessary software for running a testnet"
    )
    sub.add_argument("--configfile", type=str, required=False, default=None, help=help_config_file)
    sub.set_defaults(func=testnet_build)

    # Start
    sub = cli_shared.add_command_subparser(
        subparsers,
        "testnet",
        "start",
        "Start a testnet"
    )
    sub.add_argument("--configfile", type=str, required=False, default=None, help=help_config_file)
    sub.set_defaults(func=testnet_start)

    # Config
    sub = cli_shared.add_command_subparser(
        subparsers,
        "testnet",
        "config",
        "Configure a testnet (required before starting it the first time or after clean)"
    )
    sub.add_argument("--configfile", type=str, required=False, default=None, help=help_config_file)
    sub.set_defaults(func=testnet_config)

    # Clean
    sub = cli_shared.add_command_subparser(
        subparsers,
        "testnet",
        "clean",
        "Erase the currently configured testnet (must be already stopped)"
    )
    sub.add_argument("--configfile", type=str, required=False, default=None, help=help_config_file)
    sub.set_defaults(func=testnet_clean)


def testnet_clean(args: Any):
    logger.info("Cleaning testnet...")
    step_clean.clean(args)


def testnet_prerequisites(args: Any):
    logger.info("Gathering prerequisites...")
    step_prerequisites.prepare(args)


def testnet_build(args: Any):
    logger.info("Building binaries...")
    step_build_software.build(args)


def testnet_config(args: Any):
    logger.info("Configuring testnet...")
    step_config.configure(args)


def testnet_start(args: Any):
    logger.info("Starting testnet...")
    step_start.start(args)
