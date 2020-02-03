
import logging
import os
from os import path

from erdpy import config, environment, errors, utils

logger = logging.getLogger("builder")


def build_project(directory, debug=False):
    logger.info("build_project.directory: %s", directory)
    logger.info("build_project.debug: %s", debug)

    _guard_is_directory(directory)
    project_source = _create_project_source(directory)
    project_source.build()


def _guard_is_directory(directory):
    ok = path.isdir(directory)
    if not ok:
        raise errors.BadDirectory(directory)


def _create_project_source(directory):
    if _is_source_C(directory):
        return CProjectSource(directory)
    if _is_source_sol(directory):
        return SolProjectSource(directory)
    if _is_source_rust(directory):
        return RustProjectSource(directory)


def _is_source_C(project):
    return _project_contains_file(project, ".c")


def _is_source_sol(project):
    return _project_contains_file(project, ".sol")


def _is_source_rust(project):
    return _project_contains_file(project, "Cargo.toml")


def _project_contains_file(project, name_suffix):
    for file in os.listdir(project):
        if file.lower().endswith(name_suffix.lower()):
            return True


class ProjectSource:
    def __init__(self, directory):
        pass

    def build(self):
        dependencies = self.get_dependencies()

        # for depe
        # pass

    def get_dependencies():
        return []


class CProjectSource(ProjectSource):
    pass


class SolProjectSource(ProjectSource):
    pass


class RustProjectSource(ProjectSource):
    pass
