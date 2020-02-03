
import enum
import logging
from os import path

from erdpy.dependencies.config import get_all_modules

logger = logging.getLogger("install")


def install_group(group_name):
    logger.info(f"install_group.group_name: {group_name}")

    modules = get_modules_by_group(group_name)
    for module in modules:
        module.install()


def get_modules_by_group(group):
    return [module for module in get_all_modules() if group in module.groups]
