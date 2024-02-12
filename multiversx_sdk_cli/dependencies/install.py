import logging
from pathlib import Path
from typing import Dict, List

from multiversx_sdk_cli import config, errors
from multiversx_sdk_cli.dependencies.modules import (DependencyModule,
                                                     GolangModule, Rust,
                                                     TestWalletsModule)

logger = logging.getLogger("install")


def install_module(key: str, overwrite: bool = False):
    if key == 'all':
        modules = get_all_deps()
    else:
        modules = [get_module_by_key(key)]

    for module in modules:
        module.install(overwrite)


def get_module_directory(key: str) -> Path:
    module = get_module_by_key(key)
    default_tag = config.get_dependency_tag(key)
    directory = module.get_directory(default_tag)
    return directory


def get_module_by_key(key: str) -> DependencyModule:
    matches = [module for module in get_all_deps() if module.key == key or key in module.aliases]
    if len(matches) != 1:
        raise errors.UnknownDependency(key)

    return matches[0]


def get_deps_dict() -> Dict[str, DependencyModule]:
    deps: Dict[str, DependencyModule] = dict()

    for module in get_all_deps():
        deps[module.key] = module
        for alias in module.aliases:
            deps[alias] = module

    return deps


def get_all_deps() -> List[DependencyModule]:
    return [
        Rust(key="rust"),
        GolangModule(key="golang"),
        TestWalletsModule(key="testwallets")
    ]


def get_golang() -> GolangModule:
    golang = get_module_by_key('golang')
    assert isinstance(golang, GolangModule)
    return golang
