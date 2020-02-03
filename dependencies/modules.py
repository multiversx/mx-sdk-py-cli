
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

    def install(self):
        logger.info("install: %s / %s", self.name, self.tag)

    def uninstall(self):
        logger.info("uninstall: %s / %s", self.name, self.tag)

    def is_installed(self):
        pass


class StandaloneModule(DependencyModule):
    def __init__(self, key, name, tag, groups, urls_by_platform):
        super().__init__(key, name, tag, groups)
        self.urls_by_platform = urls_by_platform

    def install(self):
        super().install()

        platform = environment.get_platform()
        url = self.urls_by_platform.get(platform)
        url = f"{config.DOWNLOAD_MIRROR}/{url}"
        tools_folder = environment.get_tools_folder()
        archive = path.join(tools_folder, f"{self.name}.{self.tag}.tar.gz")
        downloader.download(url, archive)
        llvm_folder = path.join(tools_folder, self.name, self.tag)
        utils.untar(archive, llvm_folder)


class Rust(DependencyModule):
    def __init__(self, key, name, tag, groups):
        super().__init__(key, name, tag, groups)
