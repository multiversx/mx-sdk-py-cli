import logging
from pathlib import Path

from multiversx_sdk_cli.localnet.config_root import ConfigRoot

logger = logging.getLogger("localnet")


def new_config(configfile: Path):
    configfile = configfile.expanduser().resolve()

    if configfile.exists():
        logger.error(f"Configuration file already exists: {configfile}")
        return

    config = ConfigRoot()
    config.save(configfile)
