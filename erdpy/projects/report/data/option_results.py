from typing import Any, List, Optional

from erdpy.projects.report.data.common import first_non_none, merge_values_by_key


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

    def results_to_markdown(self) -> str:
        return ' -> '.join(self.results)


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
