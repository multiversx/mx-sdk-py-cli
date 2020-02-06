
import enum
import logging
from os import path

from erdpy.dependencies.config import get_all_modules

logger = logging.getLogger("install")


def install_group(group_name, overwrite=False):
    logger.info(f"install_group.group_name: {group_name}")

    modules = _get_modules_by_group(group_name)
    for module in modules:
        module.install(overwrite)


def install_module(key, overwrite=False):
    module = get_module_by_key(key)
    module.install(overwrite)


def get_install_directory(key):
    module = get_module_by_key(key)
    directory = module.get_directory()
    return directory


def _get_modules_by_group(group):
    return [module for module in get_all_modules() if group in module.groups]


def get_module_by_key(key):
    return [module for module in get_all_modules() if module.key == key][0]
