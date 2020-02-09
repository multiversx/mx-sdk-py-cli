
import logging
from os import path

from erdpy import errors, projects

logger = logging.getLogger("builder")


def build_project(directory, debug=False):
    logger.info("build_project.directory: %s", directory)
    logger.info("build_project.debug: %s", debug)

    _guard_is_directory(directory)
    project = projects.load_project(directory)
    project.build(debug)


def _guard_is_directory(directory):
    ok = path.isdir(directory)
    if not ok:
        raise errors.BadDirectory(directory)
