
import logging
import os
import subprocess
from os import path

from erdpy import config, downloader, environment, errors, myprocess, utils

logger = logging.getLogger("modules")


class DependencyModule:
    def __init__(self, key, name, tag, groups):
        self.key = key
        self.name = name
        self.tag = tag
        self.groups = groups

    def install(self, overwrite):
        raise NotImplementedError()

    def uninstall(self):
        raise NotImplementedError()

    def is_installed(self):
        raise NotImplementedError()


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
        folder = path.join(tools_folder, self.name, self.tag)
        return folder

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

    def install(self, overwrite):
        logger.debug(f"install: name={self.name}, tag={self.tag}")

        if self._should_skip(overwrite):
            logger.debug("Already exists. Skip install.")
            return

        rustup_path = self._get_rustup_path()
        downloader.download("https://sh.rustup.rs", rustup_path)
        utils.mark_executable(rustup_path)

        args = [rustup_path, "--verbose", "--default-toolchain", "nightly", "--profile",
                "minimal", "--target", "wasm32-unknown-unknown", "--no-modify-path", "-y"]
        myprocess.run_process_async(args, env=self.get_env())

    def _should_skip(self, overwrite):
        if overwrite:
            return False

        try:
            myprocess.run_process(["rustc", "--version"], env=self.get_env())
            return True
        except:
            return False

    def _get_rustup_path(self):
        tools_folder = environment.get_tools_folder()
        return path.join(tools_folder, "rustup.sh")

    def get_directory(self):
        tools_folder = environment.get_tools_folder()
        return path.join(tools_folder, "vendor-rust")

    def get_env(self):
        return {
            "PATH": f"{path.join(self.get_directory(), 'bin')}:{os.environ['PATH']}",
            "RUSTUP_HOME": self.get_directory(),
            "CARGO_HOME": self.get_directory()
        }
