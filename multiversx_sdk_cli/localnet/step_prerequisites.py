import logging
import shutil
import urllib.request
from typing import Any

from multiversx_sdk_cli import dependencies
from multiversx_sdk_cli.localnet.config_root import ConfigRoot
from multiversx_sdk_cli.localnet.config_software import (SoftwarePiece,
                                                         SoftwareResolution)

logger = logging.getLogger("localnet")


def prepare(args: Any):
    config = ConfigRoot.from_file(args.configfile)

    dependencies.install_module("testwallets", tag="", overwrite=True)

    if config.software.mx_chain_go.resolution == SoftwareResolution.Remote:
        download_software_piece(config.software.mx_chain_go)

    if config.software.mx_chain_proxy_go.resolution == SoftwareResolution.Remote:
        download_software_piece(config.software.mx_chain_proxy_go)

    config.software.mx_chain_go.node_config_must_exist()
    config.software.mx_chain_go.seednode_config_must_exist()
    config.software.mx_chain_proxy_go.proxy_config_must_exist()

    is_node_built = config.software.mx_chain_go.is_node_built()
    is_seednode_built = config.software.mx_chain_go.is_seednode_built()
    is_proxy_built = config.software.mx_chain_proxy_go.is_proxy_built()

    is_golang_needed = not (is_node_built and is_seednode_built and is_proxy_built)
    if is_golang_needed:
        dependencies.install_module("golang")


def download_software_piece(piece: SoftwarePiece):
    download_folder = piece.get_archive_download_folder()
    extraction_folder = piece.get_archive_extraction_folder()
    url = piece.archive_url

    shutil.rmtree(str(download_folder), ignore_errors=True)
    shutil.rmtree(str(extraction_folder), ignore_errors=True)

    download_folder.mkdir(parents=True, exist_ok=True)
    extraction_folder.mkdir(parents=True, exist_ok=True)
    archive_extension = url.split(".")[-1]
    download_path = download_folder / f"archive.{archive_extension}"

    logger.info(f"Downloading archive {url} to {download_path}")
    urllib.request.urlretrieve(url, download_path)

    logger.info(f"Unpacking archive {download_path} to {extraction_folder}")
    shutil.unpack_archive(download_path, extraction_folder, format="zip")
