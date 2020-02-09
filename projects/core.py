import logging
import os
import shutil
from os import path

from erdpy.projects.project_base import Project
from erdpy.projects.project_clang import ProjectClang
from erdpy.projects.project_rust import ProjectRust
from erdpy.projects.project_sol import ProjectSol
from erdpy.projects.templates_config import get_templates_repositories
from erdpy import errors

logger = logging.getLogger("projects.core")


def list_project_templates():
    templates = []

    for repo in get_templates_repositories():
        repo.download()
        templates.extend(repo.get_templates())

    templates = sorted(templates)
    print(templates)


def create_from_template(name, template, directory):
    logger.info("create_from_template.name: %s", name)
    logger.info("create_from_template.template: %s", template)
    logger.info("create_from_template.directory: %s", directory)

    if not directory:
        logger.info("Using current directory")
        directory = os.getcwd()

    destination_path = path.join(directory, name)

    _download_templates_repositories()
    _copy_template(template, destination_path)

    # TODO: if RUST, add tasks.json, launch.json
    # TODO: replace all placeholders

    logger.info("Project created.")


def _download_templates_repositories():
    for repo in get_templates_repositories():
        repo.download()


def _copy_template(template, destination_path):
    for repo in get_templates_repositories():
        if repo.has_template(template):
            repo.copy_template(template, destination_path)
            return

    raise errors.TemplateMissingError(template)


def load_project(directory):
    if _is_source_C(directory):
        return ProjectClang(directory)
    if _is_source_sol(directory):
        return ProjectSol(directory)
    if _is_source_rust(directory):
        return ProjectRust(directory)


def _is_source_C(directory):
    return _directory_contains_file(directory, ".c")


def _is_source_sol(directory):
    return _directory_contains_file(directory, ".sol")


def _is_source_rust(directory):
    return _directory_contains_file(directory, "Cargo.toml")


def _directory_contains_file(directory, name_suffix):
    for file in os.listdir(directory):
        if file.lower().endswith(name_suffix.lower()):
            return True
