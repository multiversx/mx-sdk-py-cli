from pathlib import Path
from typing import Any, List, Optional
from erdpy.projects.report.data.common import first_non_none, merge_values_by_key

from erdpy.projects.report.data.wasm_report import WasmReport, merge_list_of_wasms


class ProjectReport:
    def __init__(self, project_path: Path, wasms: List[WasmReport]) -> None:
        self.project_path = project_path
        self.wasms = wasms
    
    def to_json(self) -> Any:
        return {
            "project_path": str(self.project_path),
            'wasms': self.wasms
        }

    @staticmethod
    def from_json(json: Any) -> 'ProjectReport':
        wasms = [WasmReport.from_json(wasm) for wasm in json['wasms']]
        return ProjectReport(Path(json['project_path']), wasms)

    def get_rows_markdown(self) -> List[List[str]]:
        wasm_count = len(self.wasms)
        if wasm_count == 0:
            return [[f" - {str(self.project_path)} <no wasm present>"]]
        elif wasm_count == 1:
            return [[f" - {str(self.project_path / self.wasms[0].wasm_name)}"] + self.wasms[0].get_option_results()]
        else:
            project_path_row = [f" - {str(self.project_path)}"]
            wasm_rows = [[f" - - {wasm.wasm_name}"] + wasm.get_option_results() for wasm in self.wasms]
            return [project_path_row] + wasm_rows


def merge_list_of_projects(first: List[ProjectReport], second: List[ProjectReport]) -> List[ProjectReport]:
    return merge_values_by_key(first, second, get_project_report_path, merge_two_project_reports)


def get_project_report_path(project_report: ProjectReport) -> Path:
    return project_report.project_path


def merge_two_project_reports(first: Optional[ProjectReport], second: Optional[ProjectReport]) -> ProjectReport:
    if first is None or second is None:
        return first_non_none(first, second)
    merged_wasms = merge_list_of_wasms(first.wasms, second.wasms)
    return ProjectReport(first.project_path, merged_wasms)
