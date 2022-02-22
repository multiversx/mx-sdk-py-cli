from pathlib import Path
from typing import Any, List, Optional
from erdpy.projects.report.data.common import first_non_none, flatten_list_of_rows, merge_values_by_key

from erdpy.projects.report.data.project_report import ProjectReport, merge_list_of_projects


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
    
    def get_rows(self) -> List[List[str]]:
        folder_row = [str(self.root_path)]
        project_rows = flatten_list_of_rows([project.get_rows_markdown() for project in self.projects])
        return [folder_row] + project_rows


def merge_list_of_folder_reports(first: List[FolderReport], second: List[FolderReport]) -> List[FolderReport]:
    return merge_values_by_key(first, second, get_folder_report_root_path, merge_two_folder_reports)


def get_folder_report_root_path(item: FolderReport) -> Path:
    return item.root_path


def merge_two_folder_reports(first: Optional[FolderReport], second: Optional[FolderReport]) -> FolderReport:
    if first is None or second is None:
        return first_non_none(first, second)
    merged_projects = merge_list_of_projects(first.projects, second.projects)
    return FolderReport(first.root_path, merged_projects)
