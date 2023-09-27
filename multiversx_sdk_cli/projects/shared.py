import logging
import shutil
from pathlib import Path

from multiversx_sdk_cli.ux import show_critical_error

logger = logging.getLogger("projects.shared")


def is_source_clang(directory: Path) -> bool:
    return _directory_contains_file(directory, ".c")


def is_source_cpp(directory: Path) -> bool:
    return _directory_contains_file(directory, ".cpp")


def is_source_sol(directory: Path) -> bool:
    return _directory_contains_file(directory, ".sol")


def is_source_rust(directory: Path) -> bool:
    return _directory_contains_file(directory, "Cargo.toml")


def _directory_contains_file(directory: Path, name_suffix: str) -> bool:
    for file in directory.iterdir():
        if str(file).lower().endswith(name_suffix.lower()):
            return True
    return False


def are_clang_and_cpp_dependencies_installed() -> bool:
    which_clang = shutil.which("clang")
    which_llc = shutil.which("llc")
    which_wasm_ld = shutil.which("wasm-ld")
    which_llvm_link = shutil.which("llvm-link")

    logger.info(f"which_clang: {which_clang}")
    logger.info(f"which_llc: {which_llc}")
    logger.info(f"which_wasm_ld: {which_wasm_ld}")
    logger.info(f"which_llvm_link: {which_llvm_link}")

    dependencies = [which_clang, which_llc, which_wasm_ld, which_llvm_link]
    is_installed = all(dependency is not None for dependency in dependencies)
    if is_installed:
        return True

    message = """
`clang` is not installed. Please install it manually, then try again.
How to install on Ubuntu: https://linux.how2shout.com/how-to-install-clang-on-ubuntu-linux/
How to install on MacOS: https://www.incredibuild.com/integrations/clang
For more details check out this page: https://clang.llvm.org/get_started.html"""

    show_critical_error(message)
    return False
