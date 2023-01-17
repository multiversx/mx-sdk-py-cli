import logging
from pathlib import Path
from typing import Dict, List

from multiversx_sdk_cli import config, errors
from multiversx_sdk_cli.dependencies.modules import (CargoModule, NpmModule, TestWalletsModule, VMToolsModule,
                                                DependencyModule, GolangModule, NodejsModule, Rust, StandaloneModule)

logger = logging.getLogger("install")


def install_module(key: str, tag: str = "", overwrite: bool = False):
    if key == 'all':
        modules = _get_implicitly_installable_deps()
    else:
        modules = [get_module_by_key(key)]

    for module in modules:
        module.install(tag, overwrite)


def get_module_directory(key: str) -> Path:
    module = get_module_by_key(key)
    default_tag = config.get_dependency_tag(key)
    directory = module.get_directory(default_tag)
    return directory


def get_module_by_key(key: str) -> DependencyModule:
    matches = [module for module in _get_all_deps() if module.key == key or key in module.aliases]
    if len(matches) != 1:
        raise errors.UnknownDependency(key)

    return matches[0]


def get_deps_dict() -> Dict[str, DependencyModule]:
    deps: Dict[str, DependencyModule] = dict()

    for module in _get_all_deps():
        deps[module.key] = module
        for alias in module.aliases:
            deps[alias] = module

    return deps


def _get_all_deps() -> List[DependencyModule]:
    return _get_explicitly_installable_deps() + _get_implicitly_installable_deps()


def _get_explicitly_installable_deps() -> List[DependencyModule]:
    return [
        StandaloneModule(key="llvm", aliases=["clang", "cpp"]),
        Rust(key="rust"),
        NodejsModule(key="nodejs", aliases=[]),
        GolangModule(key="golang")
    ]


def _get_implicitly_installable_deps() -> List[DependencyModule]:
    # See: https://github.com/multiversx/mx-sdk-py-cli/pull/55

    return [
        VMToolsModule(key="vmtools"),
        StandaloneModule(key="mx_chain_go", repo_name="mx-chain-go", organisation="multiversx"),
        StandaloneModule(key="mx_chain_proxy_go", repo_name="mx-chain-proxy-go", organisation="multiversx"),
        NpmModule(key="wasm-opt"),
        CargoModule(key="twiggy"),
        TestWalletsModule(key="testwallets")
    ]


def get_golang() -> GolangModule:
    golang = get_module_by_key('golang')
    assert isinstance(golang, GolangModule)
    return golang
