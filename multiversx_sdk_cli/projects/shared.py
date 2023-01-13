from pathlib import Path


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
