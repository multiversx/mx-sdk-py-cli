
import logging
from os import path

from erdpy import config, downloader, environment, utils

logger = logging.getLogger("modules")


class DependencyModule:
    def __init__(self, key, name, tag, groups):
        self.key = key
        self.name = name
        self.tag = tag
        self.groups = groups

    def install(self, overwrite):
        pass

    def uninstall(self):
        pass

    def is_installed(self):
        pass


class StandaloneModule(DependencyModule):
    def __init__(self, key, name, tag, groups, urls_by_platform):
        super().__init__(key, name, tag, groups)
        self.urls_by_platform = urls_by_platform

    def install(self, overwrite):
        logger.debug(f"StandaloneModule.install: name={self.name}, tag={self.tag}")

        tools_folder = environment.get_tools_folder()
        destination_folder = path.join(tools_folder, self.name, self.tag)

        if path.isdir(destination_folder) and not overwrite:
            logger.debug("Already exists. Skip install.")
            return

        platform = environment.get_platform()
        url = self.urls_by_platform.get(platform)
        url = f"{config.DOWNLOAD_MIRROR}/{url}"
        archive = path.join(tools_folder, f"{self.name}.{self.tag}.tar.gz")
        downloader.download(url, archive)

        utils.untar(archive, destination_folder)


class Rust(DependencyModule):
    def __init__(self, key, name, tag, groups):
        super().__init__(key, name, tag, groups)
