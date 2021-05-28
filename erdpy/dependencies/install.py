import logging
from typing import Dict, List

from erdpy import config, errors
from erdpy.dependencies.modules import (ArwenToolsModule, DependencyModule,
                                        GolangModule, MclSignerModule,
                                        NodejsModule, Rust, StandaloneModule)

logger = logging.getLogger("install")


def install_module(key: str, tag: str = "", overwrite: bool = False):
    module = get_module_by_key(key)
    module.install(tag, overwrite)


def get_module_directory(key: str) -> str:
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
    return [
        StandaloneModule(key="llvm", aliases=["clang", "cpp"]),
        ArwenToolsModule(key="arwentools"),
        Rust(key="rust"),
        NodejsModule(key="nodejs", aliases=[]),
        StandaloneModule(key="elrond_go"),
        StandaloneModule(key="elrond_proxy_go"),
        GolangModule(key="golang"),
        MclSignerModule(key="mcl_signer")
    ]
