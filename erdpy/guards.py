from pathlib import Path
from erdpy import errors


def is_file(input: Path):
    if not input.is_file():
        raise errors.BadInputError(str(input), "is not a valid file")


def is_directory(directory: Path):
    if not directory.is_dir():
        raise errors.BadDirectory(str(directory))


def is_hex_address(input):
    is_hex_string(input)

    if len(input) != 64:
        raise errors.BadInputError(input, "is not a valid hex-encoded address")


def is_hex_string(input):
    try:
        bytearray.fromhex(input)
    except Exception:
        raise errors.BadInputError(input, "is not a valid hex-encoded string")
