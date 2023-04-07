import logging
from pathlib import Path
from typing import Any, List

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.testnet import (step_build_software, step_clean,
                                        step_config, step_prerequisites,
                                        step_start)

logger = logging.getLogger("cli.testnet")


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers,
        "localnet",
        "Set up, start and control local testnets"
    )
    subparsers = parser.add_subparsers()

    # Prerequisites
    sub = cli_shared.add_command_subparser(
        subparsers,
        "localnet",
        "prerequisites",
        "Download and verify the prerequisites for running a testnet"
    )
    add_argument_configfile(sub)
    sub.set_defaults(func=localnet_prerequisites)

    # Build
    sub = cli_shared.add_command_subparser(
        subparsers,
        "localnet",
        "build",
        "Build necessary software for running a testnet"
    )
    add_argument_configfile(sub)
    sub.set_defaults(func=localnet_build)

    # Start
    sub = cli_shared.add_command_subparser(
        subparsers,
        "localnet",
        "start",
        "Start a localnet"
    )
    add_argument_configfile(sub)
    sub.set_defaults(func=localnet_start)

    # Config
    sub = cli_shared.add_command_subparser(
        subparsers,
        "localnet",
        "config",
        "Configure a localnet (required before starting it the first time or after clean)"
    )
    add_argument_configfile(sub)
    sub.set_defaults(func=localnet_config)

    # Clean
    sub = cli_shared.add_command_subparser(
        subparsers,
        "localnet",
        "clean",
        "Erase the currently configured localnet (must be already stopped)"
    )
    add_argument_configfile(sub)
    sub.set_defaults(func=localnet_clean)


def add_argument_configfile(parser: Any):
    help_config_file = "An optional configuration file describing the localnet"
    parser.add_argument("--configfile", type=Path, required=False, default=Path("localnet.toml"), help=help_config_file)


def localnet_clean(args: Any):
    logger.info("Cleaning localnet...")
    step_clean.clean(args)


def localnet_prerequisites(args: Any):
    logger.info("Gathering prerequisites...")
    step_prerequisites.prepare(args)


def localnet_build(args: Any):
    logger.info("Building binaries...")
    step_build_software.build(args)


def localnet_config(args: Any):
    logger.info("Configuring localnet...")
    step_config.configure(args)


def localnet_start(args: Any):
    logger.info("Starting localnet...")
    step_start.start(args)
