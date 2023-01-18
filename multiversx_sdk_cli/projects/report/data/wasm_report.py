from typing import Any, List, Optional
from multiversx_sdk_cli.projects.report.data.common import first_not_none, merge_values_by_key
from multiversx_sdk_cli.projects.report.data.extracted_feature import ExtractedFeature, merge_lists_of_extracted_features
from multiversx_sdk_cli.projects.report.format.format_options import FormatOptions


class WasmReport:
    def __init__(self, wasm_name: str, extracted_features: List[ExtractedFeature]) -> None:
        self.wasm_name = wasm_name
        self.extracted_features = extracted_features

    def to_json(self) -> Any:
        return {
            'wasm_name': self.wasm_name,
            'extracted_features': self.extracted_features
        }

    @staticmethod
    def from_json(json: Any) -> 'WasmReport':
        extracted_features = [ExtractedFeature.from_json(extracted_feature) for extracted_feature in json['extracted_features']]
        return WasmReport(json['wasm_name'], extracted_features)

    def get_extracted_features_markdown(self, format_options: FormatOptions) -> List[str]:
        return [extracted_feature.results_to_markdown(format_options) for extracted_feature in self.extracted_features]


def merge_list_of_wasm_reports(first: List[WasmReport], second: List[WasmReport]) -> List[WasmReport]:
    return merge_values_by_key(first, second, _get_wasm_report_key, merge_two_wasm_reports)


def _get_wasm_report_key(wasm_report: WasmReport) -> str:
    return wasm_report.wasm_name


def _get_extracted_features_or_default(wasm: Optional[WasmReport]) -> List[ExtractedFeature]:
    if wasm is None:
        return []
    return wasm.extracted_features


def merge_two_wasm_reports(first: Optional[WasmReport], second: Optional[WasmReport]) -> WasmReport:
    any = first_not_none(first, second)
    first_extracted_features = _get_extracted_features_or_default(first)
    second_extracted_features = _get_extracted_features_or_default(second)
    merged_extracted_features = merge_lists_of_extracted_features(first_extracted_features, second_extracted_features)
    return WasmReport(any.wasm_name, merged_extracted_features)
