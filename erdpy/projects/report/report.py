from io import StringIO
import itertools
import json
import logging
import operator
from pathlib import Path
from typing import Any, Iterable, List, Tuple

from erdpy import guards
from erdpy.projects.core import get_project_paths_recursively, load_project
from erdpy.projects.project_base import remove_suffix
from erdpy.projects.project_rust import ProjectRust
from erdpy.projects.report.options.builder import get_default_report_options
from erdpy.projects.report.options.report_option import ReportOption
from erdpy.projects.report.options.twiggy_paths_check import run_twiggy_paths


logger = logging.getLogger("report")

def print_strings(strings: List[str]) -> None:
    joined_strings = " ".join(strings)
    print(joined_strings)


def group_projects_by_folder(project_paths: List[Path]) -> Iterable[Tuple[Path, Iterable[Tuple[Path, Path]]]]:
    path_pairs = sorted([(path.parent, path) for path in project_paths])
    return itertools.groupby(path_pairs, operator.itemgetter(0))


class OptionResult:
    def __init__(self, option_name: str, result: str) -> None:
        self.option_name = option_name
        self.result = result

    def toJson(self) -> Any:
        return {
            'option_name': self.option_name,
            'result': self.result
        }

class WasmReport:
    def __init__(self, wasm_name: str, option_results: List[OptionResult]) -> None:
        self.wasm_name = wasm_name
        self.option_results = option_results

    def toJson(self) -> Any:
        return {
            'wasm_name': self.wasm_name,
            'option_results': self.option_results
        }
    
    def get_option_results(self) -> List[str]:
        return [option.result for option in self.option_results]


class ProjectReport:
    def __init__(self, project_path: Path, wasms: List[WasmReport]) -> None:
        self.project_path = project_path
        self.wasms = wasms
    
    def toJson(self) -> Any:
        return {
            "project_path": str(self.project_path),
            'wasms': self.wasms
        }

    def get_rows(self) -> List[List[str]]:
        wasm_count = len(self.wasms)
        if wasm_count == 0:
            return [[f" - {str(self.project_path)} <no wasm present>"]]
        elif wasm_count == 1:
            return [[f" - {str(self.project_path / self.wasms[0].wasm_name)}"] + self.wasms[0].get_option_results()]
        else:
            project_path_row = [f" - {str(self.project_path)}"]
            wasm_rows = [[f" - - {wasm.wasm_name}"] + wasm.get_option_results() for wasm in self.wasms]
            return [project_path_row] + wasm_rows


class FolderReport:
    def __init__(self, root_path: Path, projects: List[ProjectReport]) -> None:
        self.root_path = root_path
        self.projects = projects

    def toJson(self) -> Any:
        return {
            'root_path': str(self.root_path),
            'projects': self.projects
        }
    
    def get_rows(self) -> List[List[str]]:
        folder_row = [str(self.root_path)]
        project_rows = flatten_list_of_rows([project.get_rows() for project in self.projects])
        return [folder_row] + project_rows


def flatten_list_of_rows(list_of_rows: List[List[List[str]]]) -> List[List[str]]:
    return list(itertools.chain(*list_of_rows))

def format_row_markdown(row: List[str]) -> str:
    row += [''] * (4 - len(row))
    row[0] = row[0].ljust(80)
    row[1] = row[1].rjust(15)
    row[2] = row[2].rjust(15)
    row[3] = row[3].rjust(15)
    merged_cells = " | ".join(row)
    return f"| {merged_cells} |"

def write_markdown_row(string: StringIO, row: List[str]):
    string.write(format_row_markdown(row))
    string.write('\n')

class Report:
    def __init__(self, options: List[ReportOption], folders: List[FolderReport]) -> None:
        self.option_names = [option.name for option in options]
        self.folders = folders
    
    def toJson(self) -> Any:
        return {
            'options': self.option_names,
            'folders': self.folders
        }
    
    def get_rows(self) -> List[List[str]]:
        rows = [group.get_rows() for group in self.folders]
        return flatten_list_of_rows(rows)

    def toMarkdown(self) -> str:
        string = StringIO()

        table_header = ["Path"] + self.option_names
        write_markdown_row(string, table_header)

        ALIGN_LEFT = ":--"
        ALIGN_RIGHT = "--:"
        row_alignments = [ALIGN_LEFT] + len(self.option_names) * [ALIGN_RIGHT]
        write_markdown_row(string, row_alignments)

        for row in self.get_rows():
            write_markdown_row(string, row)

        return string.getvalue()

    def toJsonString(self) -> str:
        return json.dumps(self, indent=4, default=lambda obj: obj.toJson())


class ReportCreator:
    def __init__(self, options: List[ReportOption], skip_build: bool, skip_twiggy: bool) -> None:
        self.options = options
        self.skip_build = skip_build
        self.skip_twiggy = skip_twiggy
        self.require_twiggy_paths = any(option.requires_twiggy_paths() for option in self.options)


    def apply_option(self, option: ReportOption, wasm_path: Path) -> OptionResult:
        result = option.apply(wasm_path)
        return OptionResult(option.name, result)


    def create_wasm_report(self, wasm_path: Path, twiggy_requirements_met: bool) -> WasmReport:
        if twiggy_requirements_met:
            run_twiggy_paths(wasm_path)
        name = wasm_path.name
        option_results = [self.apply_option(option, wasm_path) for option in self.options]
        return WasmReport(name, option_results)


    def create_project_report(self, parent_path: Path, project_path: Path) -> ProjectReport:
        project_path = project_path.resolve()
        project = load_project(project_path)

        if not self.skip_build:
            project.build()

        twiggy_requirements_met = False
        should_build_twiggy = self.require_twiggy_paths and not self.skip_twiggy
        if should_build_twiggy and isinstance(project, ProjectRust):
            project.build_wasm_with_debug_symbols()
            twiggy_requirements_met = True

        wasm_reports = [self.create_wasm_report(wasm_path, twiggy_requirements_met) for wasm_path in project.find_wasm_files()]
        wasm_reports.sort(key=lambda report: remove_suffix(report.wasm_name, '.wasm'))

        return ProjectReport(project_path.relative_to(parent_path), wasm_reports)


    def create_folder_report(self, base_path: Path, parent_folder: Path, iter: Iterable[Tuple[Path, Path]]) -> FolderReport:
        parent_folder = parent_folder.resolve()
        project_reports = [self.create_project_report(parent_folder, project_path) for _, project_path in iter]

        root_path = parent_folder.relative_to(base_path.parent)
        return FolderReport(root_path, project_reports)


    def create_report(self, base_path: Path, project_paths: List[Path]) -> Report:
        base_path = base_path.resolve()
        guards.is_directory(base_path)

        folder_groups = [self.create_folder_report(base_path, parent_folder, iter)
                            for parent_folder, iter in group_projects_by_folder(project_paths)]

        return Report(self.options, folder_groups)


def report_cli(args: Any) -> None:
    base_path = Path(args.project)
    project_paths = get_project_paths_recursively(base_path)
    options = get_default_report_options()
    report_creator = ReportCreator(options, skip_build=args.skip_build, skip_twiggy=args.skip_twiggy)
    report = report_creator.create_report(base_path, project_paths)
    if args.output_format == "markdown":
        print(report.toMarkdown())
    elif args.output_format == "json":
        print(report.toJsonString())
