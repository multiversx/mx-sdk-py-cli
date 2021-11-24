import itertools
import operator
from erdpy import dependencies
import logging
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Tuple
from pathlib import Path

from erdpy import errors, utils, guards
from erdpy.projects import shared
from erdpy.projects.project_base import Project
from erdpy.projects.project_clang import ProjectClang
from erdpy.projects.project_cpp import ProjectCpp
from erdpy.projects.project_rust import ProjectRust
from erdpy.projects.project_sol import ProjectSol

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
    output_wasm_file = project.build(options)
    logger.info("Build ran.")
    relative_wasm_path = output_wasm_file.relative_to(Path.cwd())
    logger.info(f"WASM file generated: {relative_wasm_path}")


def clean_project(directory: Path):
    directory = directory.expanduser()
    guards.is_directory(directory)
    project = load_project(directory)
    project.clean()
    logger.info("Project cleaned.")


def group_projects_by_folder(project_paths: List[Path]) -> itertools.groupby[Path, Tuple[Path, Path]]:
    path_pairs = [(path.parent, path) for path in project_paths]
    path_pairs.sort()
    return itertools.groupby(path_pairs, operator.itemgetter(0))


def report_name(project: Project) -> str:
    return project.path.name


def str_or_default(field: Optional[Any], default: str = '-') -> str:
    if field is None:
        return default
    return str(field)


def report_size(project: Project) -> str:
    size = project.get_wasm_size()
    return str_or_default(size)


def report_has_allocator(project: Project) -> str:
    has_allocator = project.check_allocator()
    return str_or_default(has_allocator)


def print_strings(strings: List[str]) -> None:
    joined_strings = " ".join(strings)
    print(joined_strings)


class ReportOption:
    def __init__(self, name: str, call: Callable[[Project], str]) -> None:
        self.name = name
        self.call = call


def build_report_options(all: bool, size: bool, has_allocator: bool) -> List[ReportOption]:
    options = [ReportOption("name", report_name)]
    if size or all:
        options.append(ReportOption("size", report_size))
    if has_allocator or all:
        options.append(ReportOption("has_allocator", report_has_allocator))
    return options


def print_report(base_path: Path, project_paths: List[Path], options: List[ReportOption]) -> None:
    base_path = base_path.resolve()

    option_names = [option.name for option in options]
    print_strings(option_names)

    for parent_folder, iter in group_projects_by_folder(project_paths):
        print(f"{parent_folder.relative_to(base_path)}:")

        for _, project_path in iter:
            project_path = project_path.expanduser()
            project = load_project(project_path)

            outputs = [option.call(project) for option in options]
            print_strings(outputs)

        print()


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
    path_list = [elrond_json.parent for elrond_json in base_path.glob("**/elrond.json")]
    return sorted(path_list)
