
import logging
from os import path

from erdpy import config, downloader, environment, errors, utils

logger = logging.getLogger("dependencies")


def install(module):
    logger.info(f"install.module: {module}")

    if module == "C":
        install_llvm("v9")
    elif module == "soll":
        install_llvm("v8")
        pass
    elif module == "rust":
        pass
    elif module == "nodedebug":
        pass
    else:
        raise errors.KnownError("Unknown module to install")

    logger.info(f"Installed [{module}]")


def install_llvm(version="v9"):
    logger.info("install_llvm.version: %s", version)

    url = _get_url_llvm(version)
    tools_folder = environment.get_tools_folder()
    archive = path.join(tools_folder, "vendor-llvm.v9.tar.gz")
    downloader.download(url, archive)
    llvm_folder = path.join(tools_folder, "llvm-folder")
    utils.untar(archive, llvm_folder)


def _get_url_llvm(version):
    root_url = f"{config.DOWNLOAD_MIRROR}/vendor-llvm/{version}"

    urls = {
        "linux": f"{root_url}/linux-amd64.tar.gz",
        "osx": f"{root_url}/darwin-amd64.tar.gz",
        "windows": f"{root_url}/windows-amd64.tar.gz",
    }

    platform = environment.get_platform()
    url = urls.get(platform)
    return url
