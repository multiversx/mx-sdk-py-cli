import os
from pathlib import Path
from typing import Union


def is_source_clang(directory: Union[Path, str]):
    return _directory_contains_file(directory, ".c")


def is_source_cpp(directory: Union[Path, str]):
    return _directory_contains_file(directory, ".cpp")


def is_source_sol(directory: Union[Path, str]):
    return _directory_contains_file(directory, ".sol")


def is_source_rust(directory: Union[Path, str]):
    return _directory_contains_file(directory, "Cargo.toml")


def _directory_contains_file(directory: Union[Path, str], name_suffix: str):
    for file in os.listdir(directory):
        if file.lower().endswith(name_suffix.lower()):
            return True
