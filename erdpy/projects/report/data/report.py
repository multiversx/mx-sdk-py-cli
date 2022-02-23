import functools
from io import StringIO
import json
from pathlib import Path
from typing import Any, List
from erdpy.projects.report.data.folder_report import FolderReport, merge_list_of_folder_reports

from erdpy.projects.report.data.common import flatten_list_of_rows, merge_values


class Report:
    def __init__(self, option_names: List[str], folders: List[FolderReport]) -> None:
        self.option_names = option_names
        self.folders = folders
    

    def to_json(self) -> Any:
        return {
            'options': self.option_names,
            'folders': self.folders
        }
    

    @staticmethod
    def from_json(json: Any) -> 'Report':
        folders = [FolderReport.from_json(folder_report) for folder_report in json['folders']]
        return Report(json['options'], folders)
    

    @staticmethod
    def load_from_file(report_json_path: Path) -> 'Report':
        with open(report_json_path, 'r') as report_file:
            report_json = json.load(report_file)
            return Report.from_json(report_json)
    

    def get_rows(self) -> List[List[str]]:
        rows = [group.get_rows() for group in self.folders]
        return flatten_list_of_rows(rows)


    def to_markdown(self) -> str:
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


    def to_json_string(self) -> str:
        return json.dumps(self, indent=4, default=lambda obj: obj.to_json())


def merge_list_of_reports(reports: List[Report]) -> Report:
    return functools.reduce(merge_two_reports, reports)


def merge_two_reports(first: Report, other: Report) -> Report:
    option_names = merge_values(first.option_names, other.option_names)
    folders = merge_list_of_folder_reports(first.folders, other.folders)
    return Report(option_names, folders)


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
