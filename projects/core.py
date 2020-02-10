import logging
import os
import shutil
from os import path
from pathlib import Path

from erdpy import errors
from erdpy.projects import shared
from erdpy.projects.project_base import Project
from erdpy.projects.project_clang import ProjectClang
from erdpy.projects.project_rust import ProjectRust
from erdpy.projects.project_sol import ProjectSol

logger = logging.getLogger("projects.core")


def load_project(directory):
    if shared.is_source_clang(directory):
        return ProjectClang(directory)
    if shared.is_source_sol(directory):
        return ProjectSol(directory)
    if shared.is_source_rust(directory):
        return ProjectRust(directory)


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
