
import logging
import os
import shutil
from os import path

from erdpy import config, downloader, environment, errors, utils
from erdpy.templates.config import get_all_repositories

logger = logging.getLogger("projects")


def create_project(name, template, directory):
    logger.info("create_project.name: %s", name)
    logger.info("create_project.template: %s", template)
    logger.info("create_project.directory: %s", directory)

    if not directory:
        logger.info("Using current directory")
        directory = os.getcwd()     

    destination_path = path.join(directory, name)

    _download_repositories()
    _copy_template(template, destination_path)

    logger.info("Project created.")


def _download_repositories():
    for repo in get_all_repositories():
        repo.download()

def _copy_template(template, destination_path):
    for repo in get_all_repositories():
        if repo.has_template(template):
            repo.copy_template(template, destination_path)
            return

    raise errors.TemplateMissingError(template)