import logging
import shutil
from pathlib import Path
from typing import Any

from multiversx_sdk_cli import dependencies, downloader
from multiversx_sdk_cli.errors import KnownError
from multiversx_sdk_cli.localnet.config_root import ConfigRoot
from multiversx_sdk_cli.localnet.config_software import SoftwareResolution

logger = logging.getLogger("localnet")


def prepare(args: Any):
    dependencies.install_module("testwallets", tag="", overwrite=True)

    config = ConfigRoot.from_file(args.configfile)
    resolution = config.software.resolution

    if resolution == SoftwareResolution.LocalPrebuiltCmdFolders:
        logger.info("Using local prebuilt CMD folders")

        subconfig = config.software.local_prebuilt_cmd_folders
        node = subconfig.ensure_mx_chain_go_node_path()
        seednode = subconfig.ensure_mx_chain_go_seednode_path()
        _proxy = subconfig.ensure_mx_chain_proxy_go_path()

        subconfig.ensure_mx_chain_go_node_config_path()
        subconfig.ensure_mx_chain_go_seednode_config_path()
        subconfig.ensure_mx_chain_proxy_go_config_path()

        for item in [node, seednode]:
            any_library = any(item.glob("*.dylib")) or any(item.glob("*.so"))

            if not any_library:
                logger.warning(f"libwasmer might be missing from {item}. Localnet might not work.")

        return

    if resolution == SoftwareResolution.LocalSourceFolders:
        logger.info("Using local source folders")

        subconfig = config.software.local_source_folders
        subconfig.ensure_mx_chain_go_path()
        subconfig.ensure_mx_chain_proxy_go_path()

        dependencies.install_module("golang")
        return

    if resolution == SoftwareResolution.RemoteArchives:
        logger.info("Using remote archives")

        subconfig = config.software.remote_archives

        _download_archive(
            url=subconfig.ensure_mx_chain_go_url(),
            archive_path=subconfig.get_mx_chain_go_archive_path(),
            destination_folder=subconfig.get_mx_chain_go_extract_path()
        )

        _download_archive(
            url=subconfig.ensure_mx_chain_proxy_go_url(),
            archive_path=subconfig.get_mx_chain_proxy_go_archive_path(),
            destination_folder=subconfig.get_mx_chain_proxy_go_extract_path()
        )

        dependencies.install_module("golang")
        return

    raise KnownError(f"Unknown software resolution: {resolution}")


def _download_archive(url: str, archive_path: Path, destination_folder: Path):
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    destination_folder.mkdir(parents=True, exist_ok=True)

    downloader.download(url, str(archive_path))
    shutil.unpack_archive(str(archive_path), str(destination_folder))
