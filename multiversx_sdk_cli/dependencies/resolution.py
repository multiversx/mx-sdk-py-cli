from enum import Enum

from multiversx_sdk_cli import config


class DependencyResolution(Enum):
    SDK = "SDK"
    Host = "Host"


def get_dependency_resolution(dependency: str) -> DependencyResolution:
    value = config.get_dependency_resolution(dependency)

    if value.lower() == "host":
        return DependencyResolution.Host
    if value.lower() == "sdk":
        return DependencyResolution.SDK

    return DependencyResolution.SDK
