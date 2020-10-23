import json
import logging
import os
import os.path
import pathlib
import shutil
import stat
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Union

import toml

from erdpy import errors

logger = logging.getLogger("utils")


class Object:
    def __repr__(self):
        return str(self.__dict__)

    def to_json(self):
        data_json = json.dumps(self.__dict__, indent=4)
        return data_json


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Object):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


def omit_fields(data: Any, fields: List[str] = []):
    if isinstance(data, dict):
        for field in fields:
            data.pop(field, None)
        return data
    raise errors.ProgrammingError("omit_fields: only dictionaries are supported.")


def untar(archive_path: str, destination_folder: str) -> None:
    logger.debug(f"untar [{archive_path}] to [{destination_folder}].")

    ensure_folder(destination_folder)
    tar = tarfile.open(archive_path)
    tar.extractall(path=destination_folder)
    tar.close()

    logger.debug("untar done.")


def unzip(archive_path, destination_folder):
    logger.debug(f"unzip [{archive_path}] to [{destination_folder}].")

    ensure_folder(destination_folder)
    with zipfile.ZipFile(archive_path, "r") as my_zip:
        my_zip.extractall(destination_folder)

    logger.debug("unzip done.")


def ensure_folder(folder: Union[str, Path]):
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)


def read_lines(file: str):
    with open(file) as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    return lines


def read_file(f: Any, binary=False) -> Union[str, bytes]:
    try:
        mode = "rb" if binary else "r"
        if isinstance(f, str) or isinstance(f, pathlib.PosixPath):
            with open(f, mode) as f:
                return f.read()
        return f.read()
    except Exception as err:
        raise errors.BadFile(f, err)


def write_file(f: Any, text: str):
    if isinstance(f, str) or isinstance(f, pathlib.PosixPath):
        with open(f, "w") as f:
            return f.write(text)
    return f.write(text)


def read_toml_file(filename):
    return toml.load(str(filename))


def write_toml_file(filename, data):
    with open(str(filename), "w") as f:
        toml.dump(data, f)


def read_json_file(filename: str) -> Dict[str, Any]:
    with open(filename) as f:
        return json.load(f)


def write_json_file(filename: str, data: Any):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def dump_out_json(data: Any, outfile: Any = None):
    if not outfile:
        outfile = sys.stdout

    json.dump(data, outfile, indent=4, cls=ObjectEncoder)
    outfile.write("\n")


def get_subfolders(folder):
    return [item.name for item in os.scandir(folder) if item.is_dir() and not item.name.startswith(".")]


def mark_executable(file: str) -> None:
    logger.debug(f"Mark [{file}] as executable")
    st = os.stat(file)
    os.chmod(file, st.st_mode | stat.S_IEXEC)


def find_in_dictionary(dictionary, compound_path):
    keys = compound_path.split(".")
    node = dictionary
    for key in keys:
        node = node.get(key)
        if node is None:
            break

    return node


def list_files(folder: str, suffix: str = None) -> List[str]:
    files = os.listdir(folder)
    files = [os.path.join(folder, f) for f in files]

    if suffix:
        files = [e for e in files if e.lower().endswith(suffix.lower())]

    return files


def remove_folder(folder):
    shutil.rmtree(folder, ignore_errors=True)


def symlink(real: str, link: str) -> None:
    if os.path.exists(link):
        os.remove(link)
    os.symlink(real, link)


def str_to_bool(input: str) -> bool:
    return str(input).lower() in ["true", "1", "t", "y", "yes"]


def as_object(input: Any) -> Object:
    if isinstance(input, dict):
        result = Object()
        result.__dict__.update(input)
        return result

    return input


def is_arg_present(key: str, args: List[str]) -> bool:
    for arg in args:
        if arg.find("--data") != -1:
            continue
        if arg.find(key) != -1:
            return True

    return False


# https://code.visualstudio.com/docs/python/debugging
# https://code.visualstudio.com/docs/python/debugging
def breakpoint():
    import debugpy
    debugpy.listen(5678)
    print("Waiting for debugger attach")
    debugpy.wait_for_client()
    debugpy.breakpoint()
