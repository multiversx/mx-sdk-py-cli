import logging
from pathlib import Path
from typing import Any, List
from erdpy import utils

from erdpy.projects.core import get_project_paths_recursively
from erdpy.projects.report.data.report import Report, merge_list_of_reports
from erdpy.projects.report.format.format_options import FormatOptions
from erdpy.projects.report.features.features import get_default_report_features
from erdpy.projects.report.report_creator import ReportCreator


logger = logging.getLogger("report")


def do_report(args: Any) -> None:
    compare_report_paths = args.compare
    if compare_report_paths is None:
        build_report(args)
    else:
        compare_reports_cli(args, compare_report_paths)


def build_report(args: Any) -> None:
    base_path = Path(args.project)
    project_paths = get_project_paths_recursively(base_path)
    options = get_default_report_features()
    report_creator = ReportCreator(options, skip_build=args.skip_build, skip_twiggy=args.skip_twiggy)
    report = report_creator.create_report(base_path, project_paths)
    finalize_report(report, args)


def compare_reports_cli(args: Any, merge_report_paths: List[Path]) -> None:
    reports = [Report.load_from_file(report_path) for report_path in merge_report_paths]
    final_report = merge_list_of_reports(reports)
    finalize_report(final_report, args)


def finalize_report(report: Report, args: Any) -> None:
    output = get_report_output_string(report, args)
    store_output(output, args)


def get_report_output_string(report: Report, args: Any) -> str:
    output_format = args.output_format
    if output_format == 'github-markdown':
        return report.to_markdown(FormatOptions(github_markdown=True))
    if output_format == 'text-markdown':
        return report.to_markdown(FormatOptions(github_markdown=False))
    elif output_format == 'json':
        return report.to_json_string()
    raise Exception('Invalid output format')


def store_output(output: str, args: Any) -> None:
    output_file_path = args.output_file
    if output_file_path is None:
        print(output)
    else:
        utils.write_file(Path(output_file_path), output)
