import logging
from pathlib import Path

logger = logging.getLogger("projects.shared")


def is_source_rust(directory: Path) -> bool:
    return _directory_contains_file(directory, "Cargo.toml")


def _directory_contains_file(directory: Path, name_suffix: str) -> bool:
    for file in directory.iterdir():
        if str(file).lower().endswith(name_suffix.lower()):
            return True
    return False
