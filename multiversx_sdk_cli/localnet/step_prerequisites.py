import logging
import shutil
from typing import Any

from multiversx_sdk_cli import dependencies, downloader
from multiversx_sdk_cli.localnet.config_root import ConfigRoot
from multiversx_sdk_cli.localnet.config_software import SoftwareResolution

logger = logging.getLogger("localnet")


def prepare(args: Any):
    config = ConfigRoot.from_file(args.configfile)

    dependencies.install_module("testwallets", tag="", overwrite=True)

    resolution_chain_go = config.software.mx_chain_go.resolution
    resolution_chain_proxy_go = config.software.mx_chain_proxy_go.resolution

    if resolution_chain_go == SoftwareResolution.Remote:
        download_folder = config.software.mx_chain_go.archive_download_folder
        extraction_folder = config.software.mx_chain_go.archive_extraction_folder
        url = config.software.mx_chain_go.archive_url

        shutil.rmtree(str(download_folder), ignore_errors=True)
        shutil.rmtree(str(extraction_folder), ignore_errors=True)

        download_folder.mkdir(parents=True, exist_ok=True)
        extraction_folder.mkdir(parents=True, exist_ok=True)
        archive_extension = url.split(".")[-1]
        download_path = download_folder / f"archive.{archive_extension}"

        downloader.download(url, str(download_path))
        shutil.unpack_archive(str(download_path), str(extraction_folder))

    if resolution_chain_proxy_go == SoftwareResolution.Remote:
        download_folder = config.software.mx_chain_proxy_go.archive_download_folder
        extraction_folder = config.software.mx_chain_proxy_go.archive_extraction_folder
        url = config.software.mx_chain_proxy_go.archive_url

        shutil.rmtree(str(download_folder), ignore_errors=True)
        shutil.rmtree(str(extraction_folder), ignore_errors=True)

        download_folder.mkdir(parents=True, exist_ok=True)
        extraction_folder.mkdir(parents=True, exist_ok=True)
        archive_extension = url.split(".")[-1]
        download_path = download_folder / f"archive.{archive_extension}"

        downloader.download(url, str(download_path))
        shutil.unpack_archive(str(download_path), str(extraction_folder))

    config.software.mx_chain_go.node_config_must_exist()
    config.software.mx_chain_go.seednode_config_must_exist()
    config.software.mx_chain_proxy_go.proxy_config_must_exist()

    is_node_built = config.software.mx_chain_go.is_node_built()
    is_seednode_built = config.software.mx_chain_go.is_seednode_built()
    is_proxy_built = config.software.mx_chain_proxy_go.is_proxy_built()

    is_golang_needed = not (is_node_built and is_seednode_built and is_proxy_built)
    if is_golang_needed:
        dependencies.install_module("golang")
