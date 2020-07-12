import os.path
from erdpy import errors


def is_file(input):
    if not os.path.isfile(input):
        raise errors.BadInputError(input, "is not a valid file")


def is_directory(directory: str):
    if not os.path.isdir(directory):
        raise errors.BadDirectory(directory)


def is_hex_address(input):
    is_hex_string(input)

    if len(input) != 64:
        raise errors.BadInputError(input, "is not a valid hex-encoded address")


def is_hex_string(input):
    try:
        bytearray.fromhex(input)
    except Exception:
        raise errors.BadInputError(input, "is not a valid hex-encoded string")
