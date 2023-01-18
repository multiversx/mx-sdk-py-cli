from pathlib import Path
from typing import Any, List, Optional
from multiversx_sdk_cli.projects.report.data.common import first_not_none, merge_values_by_key

from multiversx_sdk_cli.projects.report.data.wasm_report import WasmReport, merge_list_of_wasm_reports
from multiversx_sdk_cli.projects.report.format.format_options import FormatOptions


class ProjectReport:
    def __init__(self, project_path: Path, wasm_reports: List[WasmReport]) -> None:
        self.project_path = project_path
        self.wasm_reports = wasm_reports

    def to_json(self) -> Any:
        return {
            'project_path': str(self.project_path),
            'wasm_reports': self.wasm_reports
        }

    @staticmethod
    def from_json(json: Any) -> 'ProjectReport':
        wasm_reports = [WasmReport.from_json(wasm_report) for wasm_report in json['wasm_reports']]
        return ProjectReport(Path(json['project_path']), wasm_reports)

    def get_rows_markdown(self, format_options: FormatOptions) -> List[List[str]]:
        wasm_count = len(self.wasm_reports)
        if wasm_count == 0:
            return [[f" - {str(self.project_path)} <no wasm present>"]]
        elif wasm_count == 1:
            return [[f" - {str(self.project_path / self.wasm_reports[0].wasm_name)}"] + self.wasm_reports[0].get_extracted_features_markdown(format_options)]
        else:
            project_path_row = [f" - {str(self.project_path)}"]
            wasm_rows = [[f" - - {wasm.wasm_name}"] + wasm.get_extracted_features_markdown(format_options) for wasm in self.wasm_reports]
            return [project_path_row] + wasm_rows


def merge_list_of_projects(first: List[ProjectReport], second: List[ProjectReport]) -> List[ProjectReport]:
    return merge_values_by_key(first, second, _get_project_report_path, _merge_two_project_reports)


def _get_project_report_path(project_report: ProjectReport) -> Path:
    return project_report.project_path


def _wasm_reports_or_default(project_report: Optional[ProjectReport]) -> List[WasmReport]:
    if project_report is None:
        return []
    return project_report.wasm_reports


def _merge_two_project_reports(first: Optional[ProjectReport], second: Optional[ProjectReport]) -> ProjectReport:
    any = first_not_none(first, second)
    first_wasm_reports = _wasm_reports_or_default(first)
    second_wasm_reports = _wasm_reports_or_default(second)
    merged_wasm_reports = merge_list_of_wasm_reports(first_wasm_reports, second_wasm_reports)
    return ProjectReport(any.project_path, merged_wasm_reports)
