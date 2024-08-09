import logging
from pathlib import Path

from multiversx_sdk_cli.localnet.config_root import ConfigRoot

logger = logging.getLogger("localnet")


def new_config(configfile: Path):
    logger.info("new_config()")

    configfile = configfile.expanduser().resolve()

    if configfile.exists():
        logger.info(f"Configuration file already exists: {configfile}")
        return

    config = ConfigRoot()
    config.save(configfile)
