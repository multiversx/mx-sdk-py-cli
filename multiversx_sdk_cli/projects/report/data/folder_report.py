from pathlib import Path
from typing import Any, List, Optional
from multiversx_sdk_cli.projects.report.data.common import first_not_none, flatten_list_of_rows, merge_values_by_key

from multiversx_sdk_cli.projects.report.data.project_report import ProjectReport, merge_list_of_projects
from multiversx_sdk_cli.projects.report.format.format_options import FormatOptions


class FolderReport:
    def __init__(self, root_path: Path, projects: List[ProjectReport]) -> None:
        self.root_path = root_path
        self.projects = projects

    def to_json(self) -> Any:
        return {
            'root_path': str(self.root_path),
            'projects': self.projects
        }

    def from_json(json: Any) -> 'FolderReport':
        projects = [ProjectReport.from_json(project) for project in json['projects']]
        return FolderReport(Path(json['root_path']), projects)

    def get_markdown_rows(self, format_options: FormatOptions) -> List[List[str]]:
        folder_row = [str(self.root_path)]
        project_rows = flatten_list_of_rows([project.get_rows_markdown(format_options) for project in self.projects])
        return [folder_row] + project_rows


def merge_list_of_folder_reports(first: List[FolderReport], second: List[FolderReport]) -> List[FolderReport]:
    return merge_values_by_key(first, second, _get_folder_report_root_path, _merge_two_folder_reports)


def _get_folder_report_root_path(item: FolderReport) -> Path:
    return item.root_path


def _projects_or_default(folder_report: Optional[FolderReport]) -> List[ProjectReport]:
    if folder_report is None:
        return []
    return folder_report.projects


def _merge_two_folder_reports(first: Optional[FolderReport], second: Optional[FolderReport]) -> FolderReport:
    any = first_not_none(first, second)
    first_projects = _projects_or_default(first)
    second_projects = _projects_or_default(second)
    merged_projects = merge_list_of_projects(first_projects, second_projects)
    return FolderReport(any.root_path, merged_projects)
