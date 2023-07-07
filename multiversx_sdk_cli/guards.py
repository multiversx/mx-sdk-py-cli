from pathlib import Path

from multiversx_sdk_cli import errors


def is_file(input: Path):
    if not input.is_file():
        raise errors.BadInputError(str(input), "is not a valid file")


def is_directory(directory: Path):
    if not directory.is_dir():
        raise errors.BadDirectory(str(directory))
