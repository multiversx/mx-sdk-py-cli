
import itertools
import operator
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from multiversx_sdk_cli import guards
from multiversx_sdk_cli.projects.report.data.folder_report import FolderReport
from multiversx_sdk_cli.projects.report.data.extracted_feature import ExtractedFeature
from multiversx_sdk_cli.projects.report.data.report import Report
from multiversx_sdk_cli.projects.report.data.wasm_report import WasmReport
from multiversx_sdk_cli.projects.report.data.project_report import ProjectReport
from multiversx_sdk_cli.projects.core import load_project
from multiversx_sdk_cli.projects.project_base import remove_suffix
from multiversx_sdk_cli.projects.project_rust import ProjectRust

from multiversx_sdk_cli.projects.report.features.report_option import ReportFeature
from multiversx_sdk_cli.projects.report.features.twiggy_paths_check import run_twiggy_paths


class ReportCreator:
    def __init__(self, options: List[ReportFeature], skip_build: bool, skip_twiggy: bool, build_options: Dict[str, Any]) -> None:
        self.report_features = options
        self.skip_build = skip_build
        self.skip_twiggy = skip_twiggy
        self.require_twiggy_paths = any(report_feature.requires_twiggy_paths() for report_feature in self.report_features)
        self.build_options = build_options

    def create_report(self, base_path: Path, project_paths: List[Path]) -> Report:
        base_path = base_path.resolve()
        guards.is_directory(base_path)

        folder_groups = [self._create_folder_report(base_path, parent_folder, iter)
                         for parent_folder, iter in _group_projects_by_folder(project_paths)]

        feature_names = [report_feature.name for report_feature in self.report_features]
        return Report(feature_names, folder_groups)

    def _create_folder_report(self, base_path: Path, parent_folder: Path, iter: Iterable[Tuple[Path, Path]]) -> FolderReport:
        parent_folder = parent_folder.resolve()
        project_reports = [self._create_project_report(parent_folder, project_path) for _, project_path in iter]

        root_path = parent_folder.relative_to(base_path.parent)
        return FolderReport(root_path, project_reports)

    def _create_project_report(self, parent_path: Path, project_path: Path) -> ProjectReport:
        project_path = project_path.resolve()
        project = load_project(project_path)

        if not self.skip_build:
            project.build(self.build_options)

        twiggy_requirements_met = False
        should_build_twiggy = self.require_twiggy_paths and not self.skip_twiggy
        if should_build_twiggy and isinstance(project, ProjectRust):
            project.build_wasm_with_debug_symbols(self.build_options)
            twiggy_requirements_met = True

        wasm_reports = [self._create_wasm_report(wasm_path, twiggy_requirements_met) for wasm_path in project.find_wasm_files()]
        wasm_reports.sort(key=lambda report: remove_suffix(report.wasm_name, '.wasm'))

        return ProjectReport(project_path.relative_to(parent_path), wasm_reports)

    def _create_wasm_report(self, wasm_path: Path, twiggy_requirements_met: bool) -> WasmReport:
        if twiggy_requirements_met:
            run_twiggy_paths(wasm_path)
        name = wasm_path.name
        extracted_features = [_extract_feature(report_feature, wasm_path) for report_feature in self.report_features]
        return WasmReport(name, extracted_features)


def _extract_feature(feature: ReportFeature, wasm_path: Path) -> ExtractedFeature:
    result = feature.extract(wasm_path)
    return ExtractedFeature(feature.name, [result])


def _group_projects_by_folder(project_paths: List[Path]) -> Iterable[Tuple[Path, Iterable[Tuple[Path, Path]]]]:
    path_pairs = sorted([(path.parent, path) for path in project_paths])
    return itertools.groupby(path_pairs, operator.itemgetter(0))
