
import logging
from os import path

from erdpy import config, downloader, environment, errors, utils

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
        logger.debug(f"install: name={self.name}, tag={self.tag}")

        if self._should_skip(overwrite):
            logger.debug("Already exists. Skip install.")
            return

        self._download()
        self._extract()

    def _should_skip(self, overwrite):
        if overwrite:
            return False

        destination_folder = self.get_directory()
        exists = path.isdir(destination_folder)
        return exists

    def _download(self):
        url = self._get_download_url()
        archive_path = self._get_archive_path()
        downloader.download(url, archive_path)

    def _extract(self):
        archive_path = self._get_archive_path()
        destination_folder = self.get_directory()
        utils.untar(archive_path, destination_folder)

    def get_directory(self):
        tools_folder = environment.get_tools_folder()
        destination_folder = path.join(tools_folder, self.name, self.tag)
        return destination_folder

    def _get_download_url(self):
        platform = environment.get_platform()
        url = self.urls_by_platform.get(platform)

        if url is None:
            raise errors.PlatformNotSupported(self.name, platform)

        url = f"{config.DOWNLOAD_MIRROR}/{url}"
        return url

    def _get_archive_path(self):
        tools_folder = environment.get_tools_folder()
        archive = path.join(tools_folder, f"{self.name}.{self.tag}.tar.gz")
        return archive


class Rust(DependencyModule):
    def __init__(self, key, name, tag, groups):
        super().__init__(key, name, tag, groups)
