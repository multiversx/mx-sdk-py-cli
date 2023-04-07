import logging
from typing import Any

from multiversx_sdk_cli import utils
from multiversx_sdk_cli.testnet.config import TestnetConfiguration

logger = logging.getLogger("localnet")


def clean(args: Any):
    config = TestnetConfiguration.from_file(args.configfile)
    utils.remove_folder(config.root())
