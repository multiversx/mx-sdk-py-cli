from erdpy import dependencies
import logging
from os import path
from typing import Any, Dict
from pathlib import Path

from erdpy import errors, utils, guards
from erdpy.projects import shared
from erdpy.projects.project_clang import ProjectClang
from erdpy.projects.project_cpp import ProjectCpp
from erdpy.projects.project_rust import ProjectRust
from erdpy.projects.project_sol import ProjectSol

logger = logging.getLogger("projects.core")


def load_project(directory):
    guards.is_directory(directory)

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


def build_project(directory: str, options: Dict[str, Any]):
    directory = path.expanduser(directory)

    logger.info("build_project.directory: %s", directory)
    logger.info("build_project.debug: %s", options['debug'])

    guards.is_directory(directory)
    project = load_project(directory)
    output_wasm_file = project.build(options)
    logger.info("Build ran.")
    relative_wasm_path = output_wasm_file.relative_to(Path.cwd())
    logger.info(f"WASM file generated: {relative_wasm_path}")


def clean_project(directory: str):
    directory = path.expanduser(directory)
    guards.is_directory(directory)
    project = load_project(directory)
    project.clean()
    logger.info("Project cleaned.")


def run_tests(args: Any):
    project = args.project
    directory = args.directory
    wildcard = args.wildcard

    logger.info("run_tests.project: %s", project)

    dependencies.install_module("vmtools")

    guards.is_directory(project)
    project = load_project(project)
    project.run_tests(directory, wildcard)


def get_projects_in_workspace(workspace):
    guards.is_directory(workspace)
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
