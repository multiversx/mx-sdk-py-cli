from collections import OrderedDict
import itertools
from typing import Callable, List, Optional, TypeVar


def flatten_list_of_rows(list_of_rows: List[List[List[str]]]) -> List[List[str]]:
    return list(itertools.chain(*list_of_rows))


def merge_values(first: List[str], second: List[str]) -> List[str]:
    return list(OrderedDict.fromkeys(first + second))


T = TypeVar('T')
K = TypeVar('K')


def first_not_none(first: Optional[T], second: Optional[T]) -> T:
    return next(item for item in [first, second] if item is not None)


def get_keys(items: List[T], key_getter: Callable[[T], K]) -> List[K]:
    return [key_getter(item) for item in items]


def list_as_key_value_dict(items: List[T], key_getter: Callable[[T], K]) -> 'OrderedDict[K, T]':
    return OrderedDict(zip(get_keys(items, key_getter), items))


def merge_values_by_key(first: List[T], second: List[T], key_getter: Callable[[T], K], merge: Callable[[Optional[T], Optional[T]], T]) -> List[T]:
    first_as_dict = list_as_key_value_dict(first, key_getter)
    second_as_dict = list_as_key_value_dict(second, key_getter)
    union = OrderedDict.fromkeys(list(first_as_dict.keys()) + list(second_as_dict.keys()))
    all_keys = union.keys()
    result = []
    for key in all_keys:
        first_value = first_as_dict.get(key)
        second_value = second_as_dict.get(key)
        result.append(merge(first_value, second_value))
    return result
