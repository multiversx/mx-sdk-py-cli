from typing import Any, List, Optional

from multiversx_sdk_cli.projects.report.data.common import first_not_none, merge_values_by_key
from multiversx_sdk_cli.projects.report.format.change_type import ChangeType
from multiversx_sdk_cli.projects.report.format.format_options import FormatOptions


class ExtractedFeature:
    def __init__(self, feature_name: str, results: List[str]) -> None:
        self.feature_name = feature_name
        self.results = results

    def to_json(self) -> Any:
        return {
            'feature_name': self.feature_name,
            'results': self.results
        }

    @staticmethod
    def from_json(json: Any) -> 'ExtractedFeature':
        return ExtractedFeature(json['feature_name'], json['results'])

    def results_to_markdown(self, format_options: FormatOptions) -> str:
        separator = ' :arrow_right: ' if format_options.github_flavor else ' -> '
        change_type = self._classify_changes()
        display_results = _prepare_results_for_markdown(self.results)
        if change_type == ChangeType.NONE:
            return display_results[0]
        else:
            return separator.join(display_results) + ' ' + change_type.to_markdown(format_options)

    def _classify_changes(self) -> ChangeType:
        """
        Used to classify if a change in a feature's results is good, bad etc.
        Required because changes in values are not always intuitive:
        - a higher value may be worse than a small one (eg. for file sizes)
        - a 'Yes' may be worse than a 'No'
        This information is used to draw small icons at the end of a cell containing a change.
        """

        all_results_are_identical = all(result == self.results[0] for result in self.results)
        if all_results_are_identical:
            return ChangeType.NONE
        any_is_not_available = any(result == 'N/A' for result in self.results)
        if any_is_not_available:
            return ChangeType.UNKNOWN
        if self.feature_name == 'size':
            sizes = list(map(int, self.results))
            return _classify_list(sizes, reverse=True)
        if self.feature_name == 'has-allocator' or self.feature_name == 'has-format':
            presence_checks = list(map(lambda value: False if value == 'False' else True, self.results))
            return _classify_list(presence_checks, reverse=True)
        return ChangeType.UNKNOWN


def _prepare_results_for_markdown(results: List[str]) -> List[str]:
    return list(map(_replace_bool_with_yes_no, results))


def _replace_bool_with_yes_no(item: str) -> str:
    if item == 'True':
        return 'Yes'
    if item == 'False':
        return 'No'
    return item


def _classify_list(items: List[Any], reverse: bool = False) -> ChangeType:
    if reverse:
        items.reverse()
    if _is_strictly_better(items):
        return ChangeType.GOOD
    if _is_strictly_worse(items):
        return ChangeType.BAD
    return ChangeType.MIXED


def _is_strictly_better(items: List[Any]) -> bool:
    return sorted(items) == items


def _is_strictly_worse(items: List[Any]) -> bool:
    return sorted(items, reverse=True) == items


def merge_lists_of_extracted_features(first: List[ExtractedFeature], second: List[ExtractedFeature]) -> List[ExtractedFeature]:
    return merge_values_by_key(first, second, _get_extracted_feature_key, _merge_two_extracted_features)


def _get_extracted_feature_key(extracted_feature: ExtractedFeature) -> str:
    return extracted_feature.feature_name


def _merge_two_extracted_features(first: Optional[ExtractedFeature], second: Optional[ExtractedFeature]) -> ExtractedFeature:
    any = first_not_none(first, second)
    merged_results = _results_or_NA(first) + _results_or_NA(second)
    return ExtractedFeature(any.feature_name, merged_results)


def _results_or_NA(extracted_feature: Optional[ExtractedFeature]) -> List[str]:
    if extracted_feature is None:
        return ['N/A']
    else:
        return extracted_feature.results
