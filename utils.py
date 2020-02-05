import logging
import os
import pathlib
import stat
import subprocess
import tarfile
import zipfile

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


def run_process(args):
    logger.info(f"run_process: {args}")

    output = subprocess.check_output(args, shell=False, universal_newlines=True, stderr=subprocess.STDOUT)
    logger.info("Successful run. Output:")
    print(output or "[No output]")
    return output
    

def read_lines(file):
    with open(file) as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    return lines


def get_subfolders(folder):
    return [item.name for item in os.scandir(folder) if item.is_dir() and not item.name.startswith(".")]
