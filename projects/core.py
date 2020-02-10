import logging
import os
import shutil
from os import path
from pathlib import Path

from erdpy import errors
from erdpy.projects.project_base import Project
from erdpy.projects.project_clang import ProjectClang
from erdpy.projects.project_rust import ProjectRust
from erdpy.projects.project_sol import ProjectSol
from erdpy.projects.templates_config import get_templates_repositories

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

    project_directory = path.join(directory, name)

    _download_templates_repositories()
    _copy_template(template, project_directory)
    _expand_template(project_directory)
    _supplant_template_placeholders(project_directory)

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


def _expand_template(directory):
    if _is_source_clang(directory):
        _expand_template_clang(directory)
    if _is_source_sol(directory):
        _expand_template_sol(directory)
    if _is_source_rust(directory):
        _expand_template_rust(directory)


def _expand_template_clang(directory):
    pass


def _expand_template_sol(directory):
    pass


def _expand_template_rust(directory):
    logger.info("_expand_template_rust")

    package_path = Path(__file__).parent
    launch_file = package_path.joinpath("vscode_launch_rust.json")
    tasks_file = package_path.joinpath("vscode_tasks_rust.json")
    vscode_directory = path.join(directory, ".vscode")

    logger.info("Creating directory [.vscode]...")
    os.mkdir(vscode_directory)
    logger.info("Adding files: [launch.json], [tasks.json]")
    shutil.copy(launch_file, path.join(vscode_directory, "launch.json"))
    shutil.copy(tasks_file, path.join(vscode_directory, "tasks.json"))


def _supplant_template_placeholders(directory):
    pass


def load_project(directory):
    if _is_source_clang(directory):
        return ProjectClang(directory)
    if _is_source_sol(directory):
        return ProjectSol(directory)
    if _is_source_rust(directory):
        return ProjectRust(directory)


def _is_source_clang(directory):
    return _directory_contains_file(directory, ".c")


def _is_source_sol(directory):
    return _directory_contains_file(directory, ".sol")


def _is_source_rust(directory):
    return _directory_contains_file(directory, "Cargo.toml")


def _directory_contains_file(directory, name_suffix):
    for file in os.listdir(directory):
        if file.lower().endswith(name_suffix.lower()):
            return True


def build_project(directory, debug=False):
    logger.info("build_project.directory: %s", directory)
    logger.info("build_project.debug: %s", debug)

    _guard_is_directory(directory)
    project = load_project(directory)
    project.build(debug)


def _guard_is_directory(directory):
    ok = path.isdir(directory)
    if not ok:
        raise errors.BadDirectory(directory)
