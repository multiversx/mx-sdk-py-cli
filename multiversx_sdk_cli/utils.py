import json
import logging
import os
import pathlib
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Optional, Protocol, Union, runtime_checkable

import toml

logger = logging.getLogger("utils")


@runtime_checkable
class ISerializable(Protocol):
    def to_dictionary(self) -> dict[str, Any]:
        return self.__dict__


class Object(ISerializable):
    def __repr__(self):
        return str(self.__dict__)

    def to_dictionary(self):
        return dict(self.__dict__)

    def to_json(self):
        data_json = json.dumps(self.__dict__, indent=4)
        return data_json


class BasicEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ISerializable):
            return o.to_dictionary()
        if isinstance(o, bytes):
            return o.hex()
        # needed because sdk-py returns SimpleNamespace objects that the json library does not know to serialize
        if isinstance(o, SimpleNamespace):
            return o.__dict__
        return super().default(o)


def omit_fields(data: dict[str, Any], fields: list[str] = []) -> None:
    for field in fields:
        data.pop(field, None)


def untar(archive_path: Path, destination_folder: Path) -> None:
    logger.debug(f"untar [{archive_path}] to [{destination_folder}].")

    ensure_folder(destination_folder)
    tar = tarfile.open(str(archive_path))
    tar.extractall(path=str(destination_folder))
    tar.close()

    logger.debug("untar done.")


def unzip(archive_path: Path, destination_folder: Path):
    logger.debug(f"unzip [{archive_path}] to [{destination_folder}].")

    ensure_folder(destination_folder)
    with zipfile.ZipFile(str(archive_path), "r") as my_zip:
        my_zip.extractall(str(destination_folder))

    logger.debug("unzip done.")


def ensure_folder(folder: Union[str, Path]):
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)


def read_lines(file: Path) -> list[str]:
    with open(file) as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    return lines


def write_file(file_path: Path, text: str):
    with open(file_path, "w") as file:
        return file.write(text)


def read_toml_file(filename: Union[str, Path]):
    return toml.load(str(filename))


def write_toml_file(filename: Union[str, Path], data: Any):
    with open(str(filename), "w") as f:
        toml.dump(data, f)


def read_json_file(filename: Union[str, Path]) -> Any:
    with open(filename) as f:
        return json.load(f)


def write_json_file(filename: Union[str, Path], data: Any):
    with open(str(filename), "w") as f:
        json.dump(data, f, indent=4)


def dump_out_json(data: Any, outfile: Any = None):
    if not outfile:
        outfile = sys.stdout

    json.dump(data, outfile, indent=4, cls=BasicEncoder)
    outfile.write("\n")


def get_subfolders(folder: Path) -> list[str]:
    return [item.name for item in os.scandir(folder) if item.is_dir() and not item.name.startswith(".")]


def list_files(folder: Path, suffix: Optional[str] = None) -> list[Path]:
    folder = folder.expanduser()
    files: list[Path] = [folder / file for file in os.listdir(folder)]
    files = [file for file in files if file.is_file()]

    if suffix:
        files = [file for file in files if str(file).lower().endswith(suffix.lower())]

    return files


def remove_folder(folder: Union[str, Path]):
    shutil.rmtree(folder, ignore_errors=True)


def symlink(real: str, link: str) -> None:
    if os.path.islink(link):
        os.remove(link)
    os.symlink(real, link)


def is_arg_present(args: list[str], key: str) -> bool:
    for arg in args:
        if arg.find("--data") != -1:
            continue
        if arg.find(key) != -1:
            return True

    return False


def log_explorer(name: str, explorer: str, path: str, details: str):
    logger.info(f"View this {name} in the MultiversX Explorer: {explorer}/{path}/{details}")


def log_explorer_contract_address(chain: str, address: str, explorer_url: Optional[str] = ""):
    if explorer_url:
        log_explorer("contract address", explorer_url, "accounts", address)
    else:
        explorer = get_explorer_by_chain_id(chain_id=chain)
        if explorer:
            log_explorer("contract address", explorer, "accounts", address)


def log_explorer_transaction(chain: str, transaction_hash: str, explorer_url: Optional[str] = ""):
    if explorer_url:
        log_explorer("transaction", explorer_url, "transactions", transaction_hash)
    else:
        explorer = get_explorer_by_chain_id(chain_id=chain)
        if explorer:
            log_explorer("transaction", explorer, "transactions", transaction_hash)


def get_explorer_by_chain_id(chain_id: str) -> str:
    explorers_by_chain_id = {
        "1": "https://explorer.multiversx.com",
        "T": "https://testnet-explorer.multiversx.com",
        "D": "https://devnet-explorer.multiversx.com",
    }

    try:
        return explorers_by_chain_id[chain_id]
    except KeyError:
        return ""
