import logging
from pathlib import Path
from typing import Any, Dict, List

from multiversx_sdk_cli import dependencies, errors, guards, utils
from multiversx_sdk_cli.projects import shared
from multiversx_sdk_cli.projects.constants import (OLD_PROJECT_CONFIG_FILENAME,
                                                   PROJECT_CONFIG_FILENAME)
from multiversx_sdk_cli.projects.project_base import Project
from multiversx_sdk_cli.projects.project_clang import ProjectClang
from multiversx_sdk_cli.projects.project_cpp import ProjectCpp
from multiversx_sdk_cli.projects.project_rust import ProjectRust
from multiversx_sdk_cli.projects.project_sol import ProjectSol

logger = logging.getLogger("projects.core")


def load_project(directory: Path) -> Project:
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
        raise errors.NotSupportedProject(str(directory))


def build_project(directory: Path, options: Dict[str, Any]):
    directory = directory.expanduser()

    logger.info("build_project.directory: %s", directory)
    logger.info("build_project.debug: %s", options['debug'])

    guards.is_directory(directory)
    project = load_project(directory)
    outputs = project.build(options)
    logger.info("Build ran.")
    for output_wasm_file in outputs:
        logger.info(f"WASM file generated: {output_wasm_file}")


def clean_project(directory: Path):
    logger.info("clean_project.directory: %s", directory)
    directory = directory.expanduser()
    guards.is_directory(directory)
    project = load_project(directory)
    project.clean()
    logger.info("Project cleaned.")


def run_tests(args: Any):
    project_path = Path(args.project)
    directory = Path(args.directory)
    wildcard = args.wildcard

    logger.info("run_tests.project: %s", project_path)

    dependencies.install_module("vmtools")

    guards.is_directory(project_path)
    project = load_project(project_path)
    project.run_tests(directory, wildcard)


def get_projects_in_workspace(workspace: Path) -> List[Project]:
    guards.is_directory(workspace)
    subfolders = utils.get_subfolders(workspace)
    projects = []

    for folder in subfolders:
        project_directory = workspace / folder

        try:
            project = load_project(project_directory)
            projects.append(project)
        except Exception:
            pass

    return projects


def get_project_paths_recursively(base_path: Path) -> List[Path]:
    guards.is_directory(base_path)
    old_markers = list(base_path.glob(f"**/{OLD_PROJECT_CONFIG_FILENAME}"))
    new_markers = list(base_path.glob(f"**/{PROJECT_CONFIG_FILENAME}"))
    project_marker_files = old_markers + new_markers
    path_list = [marker_file.parent for marker_file in project_marker_files]
    return sorted(path_list)
