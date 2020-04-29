import logging
from os import path

from erdpy import dependencies, errors, utils
from erdpy.projects import shared
from erdpy.projects.project_clang import ProjectClang
from erdpy.projects.project_cpp import ProjectCpp
from erdpy.projects.project_rust import ProjectRust
from erdpy.projects.project_sol import ProjectSol

logger = logging.getLogger("projects.core")


def load_project(directory):
    _guard_is_directory(directory)

    if shared.is_source_clang(directory):
        return ProjectClang(directory)
    if shared.is_source_cpp(directory):
        return ProjectCpp(directory)
    if shared.is_source_sol(directory):
        return ProjectSol(directory)
    if shared.is_source_rust(directory):
        return ProjectRust(directory)
    else:
        raise errors.NotSupportedProject(directory)


def build_project(directory, options):
    directory = path.expanduser(directory)

    logger.info("build_project.directory: %s", directory)
    logger.info("build_project.debug: %s", options['debug'])

    _guard_is_directory(directory)
    project = load_project(directory)
    project.build(options)


def _guard_is_directory(directory):
    ok = path.isdir(directory)
    if not ok:
        raise errors.BadDirectory(directory)


def run_tests(args):
    project = args.project
    directory = args.directory
    wildcard = args.wildcard

    logger.info("run_tests.project: %s", project)

    dependencies.install_module("arwentools")

    _guard_is_directory(project)
    project = load_project(project)
    project.run_tests(directory, wildcard)


def get_projects_in_workspace(workspace):
    _guard_is_directory(workspace)
    subfolders = utils.get_subfolders(workspace)
    projects = []

    for folder in subfolders:
        project_directory = path.join(workspace, folder)

        try:
            project = load_project(project_directory)
            projects.append(project)
        except Exception:
            pass

    return projects
