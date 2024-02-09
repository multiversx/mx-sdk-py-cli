import logging
from pathlib import Path
from typing import Any, List

from multiversx_sdk_cli import dependencies, errors, guards
from multiversx_sdk_cli.projects import shared
from multiversx_sdk_cli.projects.constants import (OLD_PROJECT_CONFIG_FILENAME,
                                                   PROJECT_CONFIG_FILENAME)
from multiversx_sdk_cli.projects.project_base import Project
from multiversx_sdk_cli.projects.project_rust import ProjectRust

logger = logging.getLogger("projects.core")


def load_project(directory: Path) -> Project:
    guards.is_directory(directory)

    if shared.is_source_rust(directory):
        return ProjectRust(directory)
    else:
        raise errors.NotSupportedProject(str(directory))


def build_project(directory: Path, args: List[str]):
    directory = directory.expanduser()

    logger.info("build_project.directory: %s", directory)

    project = load_project(directory)
    outputs = project.build(args)
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
    directory = Path(args.path)

    logger.info("run_tests.project: %s", directory)

    guards.is_directory(directory)
    project = load_project(directory)
    project.run_tests(args)


def get_project_paths_recursively(base_path: Path) -> List[Path]:
    guards.is_directory(base_path)
    old_markers = list(base_path.glob(f"**/{OLD_PROJECT_CONFIG_FILENAME}"))
    new_markers = list(base_path.glob(f"**/{PROJECT_CONFIG_FILENAME}"))
    project_marker_files = old_markers + new_markers
    path_list = [marker_file.parent for marker_file in project_marker_files]
    return sorted(path_list)
