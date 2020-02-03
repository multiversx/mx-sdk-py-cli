
import logging
import os
from os import path

from erdpy import config, dependencies, environment, errors, utils

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
        self._ensure_dependencies_installed()

    def _ensure_dependencies_installed(self):
        module_keys = self.get_dependencies()
        for module_key in module_keys:
            dependencies.install_module(module_key)

    def get_dependencies(self):
        return []


class CProjectSource(ProjectSource):
    def build(self):
        super().build()
        print("Build using LLVM.")

    def get_dependencies(self):
        return ["llvm-for-c"]


class SolProjectSource(ProjectSource):
    pass


class RustProjectSource(ProjectSource):
    pass
