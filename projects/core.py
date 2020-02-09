import os

from erdpy.projects import ProjectClang, ProjectRust, ProjectSol


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
