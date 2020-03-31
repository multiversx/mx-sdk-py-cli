import json
import logging
import os
import pathlib
import stat
import tarfile
import zipfile

import toml

logger = logging.getLogger("utils")


def untar(archive_path, destination_folder):
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


def ensure_folder(folder):
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)


def read_lines(file):
    with open(file) as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    return lines


def read_file(filename):
    with open(filename) as f:
        return f.read()


def write_file(filename, text):
    with open(filename, "w") as f:
        return f.write(text)


def read_toml_file(filename):
    return toml.load(filename)


def write_toml_file(filename, data):
    with open(filename, "w") as f:
        toml.dump(data, f)


def get_subfolders(folder):
    return [item.name for item in os.scandir(folder) if item.is_dir() and not item.name.startswith(".")]


def mark_executable(file):
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
