import logging
from typing import List, Union

from erdpy.projects.eei_activation import ActivationEpochsInfo


class EEIRegistry:
    def __init__(self, activation_info: ActivationEpochsInfo) -> None:
        self.activation_info = activation_info
        self.flags: List[FeatureFlag] = []
        self.functions: List[EEIFunction] = [
            # e.g. EEIFunction("foobar", FeatureFlag("fooFeature"), []),
        ]
        self.functions_dict = {function.name: function for function in self.functions}

    def sync_flags(self):
        for flag in self.flags:
            flag.sync(self.activation_info)

    def is_function_active(self, function_name: str) -> Union[bool, None]:
        function = self.functions_dict.get(function_name, None)
        if function is None:
            # If function is not found in this registry, assume it is <active> on all known networks.
            return True
        if function.activated_by is None:
            return True
        return function.activated_by.is_active


class FeatureFlag:
    def __init__(self, name: str) -> None:
        self.name = name
        self.is_active: Union[bool, None] = None

    def sync(self, activation_info: ActivationEpochsInfo):
        try:
            self.is_active = activation_info.is_flag_active(self.name)
        except Exception as err:
            self.is_active = None
            logging.error(err)


class EEIFunction:
    def __init__(self, name: str, activated_by: Union[FeatureFlag, None], tags: List[str]) -> None:
        self.name = name
        self.activated_by = activated_by
        self.tags = tags
