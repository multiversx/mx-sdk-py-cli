from typing import Any, List, Optional

from erdpy.projects.report.data.common import first_non_none, merge_values_by_key
from erdpy.projects.report.format.change_type import ChangeType
from erdpy.projects.report.format.format_options import FormatOptions


class OptionResults:
    def __init__(self, option_name: str, results: List[str]) -> None:
        self.option_name = option_name
        self.results = results


    def to_json(self) -> Any:
        return {
            'option_name': self.option_name,
            'results': self.results
        }


    @staticmethod
    def from_json(json: Any) -> 'OptionResults':
        return OptionResults(json['option_name'], json['results'])


    def results_to_markdown(self, format_options: FormatOptions) -> str:
        separator = ' :arrow_right: ' if format_options.github_flavor else ' -> '
        change_type = self.classify_changes()
        display_results = prepare_results_for_markdown(self.results)
        if change_type == ChangeType.NONE:
            return display_results[0]
        else:
            return separator.join(display_results) + ' ' + change_type.to_markdown(format_options)
    

    def classify_changes(self) -> ChangeType:
        all_results_are_identical = all(result == self.results[0] for result in self.results)
        if all_results_are_identical:
            return ChangeType.NONE
        any_is_not_available = any(result == 'N/A' for result in self.results)
        if any_is_not_available:
            return ChangeType.UNKNOWN
        if self.option_name == 'size':
            sizes = list(map(int, self.results))
            return classify_list(sizes, reverse=True)
        if self.option_name == 'has-allocator' or self.option_name == 'has-format':
            presence_checks = list(map(lambda value: False if value == 'False' else True, self.results))
            return classify_list(presence_checks, reverse=True)
        return ChangeType.UNKNOWN


def prepare_results_for_markdown(results: List[str]) -> List[str]:
    return list(map(replace_bool_with_yes_no, results))


def replace_bool_with_yes_no(item: str) -> str:
    if item == 'True':
        return 'Yes'
    if item == 'False':
        return 'No'
    return item


def classify_list(items: List[Any], reverse: bool = False) -> ChangeType:
    if reverse:
        items.reverse()
    if is_strictly_better(items):
        return ChangeType.GOOD
    if is_strictly_worse(items):
        return ChangeType.BAD
    return ChangeType.MIXED


def is_strictly_better(items: List[Any]) -> bool:
    return sorted(items) == items


def is_strictly_worse(items: List[Any]) -> bool:
    return sorted(items, reverse=True) == items


def merge_lists_of_option_results(first: List[OptionResults], second: List[OptionResults]) -> List[OptionResults]:
    return merge_values_by_key(first, second, get_option_result_key, merge_two_option_results)


def get_option_result_key(option_results: OptionResults) -> str:
    return option_results.option_name


def merge_two_option_results(first: Optional[OptionResults], second: Optional[OptionResults]) -> OptionResults:
    any = first_non_none(first, second)
    merged_results = results_or_NA(first) + results_or_NA(second)
    return OptionResults(any.option_name, merged_results)


def results_or_NA(option_result: Optional[OptionResults]) -> List[str]:
    if option_result is None:
        return ['N/A']
    else:
        return option_result.results
