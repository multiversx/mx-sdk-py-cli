import logging
from pathlib import Path
from typing import Dict, List

from erdpy import config, errors
from erdpy.dependencies.modules import (NpmModule, VMToolsModule, DependencyModule,
                                        GolangModule, MclSignerModule,
                                        NodejsModule, Rust, StandaloneModule)

logger = logging.getLogger("install")


def install_module(key: str, tag: str = "", overwrite: bool = False):
    if key == 'all':
        modules = get_all_deps_installable_via_cli()
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
    matches = [module for module in get_all_deps() if module.key == key or key in module.aliases]
    if len(matches) != 1:
        raise errors.UnknownDependency(key)

    return matches[0]


def get_deps_dict() -> Dict[str, DependencyModule]:
    deps = dict()
    for module in get_all_deps():
        deps[module.key] = module
        for alias in module.aliases:
            deps[alias] = module
    return deps


def get_all_deps() -> List[DependencyModule]:
    return get_all_implicit_deps() + get_all_deps_installable_via_cli()


def get_all_implicit_deps() -> List[DependencyModule]:
    return [
        StandaloneModule(key="llvm", aliases=["clang", "cpp"]),
        Rust(key="rust"),
        NodejsModule(key="nodejs", aliases=[]),
        GolangModule(key="golang"),
    ]


def get_all_deps_installable_via_cli() -> List[DependencyModule]:
    return [
        VMToolsModule(key="vmtools"),
        StandaloneModule(key="elrond_go", repo_name="elrond-go", organisation="ElrondNetwork"),
        StandaloneModule(key="elrond_proxy_go", repo_name="elrond-proxy-go", organisation="ElrondNetwork"),
        MclSignerModule(key="mcl_signer"),
        NpmModule(key="wasm-opt")
    ]



def get_golang() -> GolangModule:
    golang = get_module_by_key('golang')
    assert isinstance(golang, GolangModule)
    return golang
