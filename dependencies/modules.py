
import logging
import os
import shutil
from os import path
from typing import Dict, List

from erdpy import config, downloader, errors, myprocess, utils, workstation

logger = logging.getLogger("modules")


class DependencyModule:
    def __init__(self, key: str, aliases: List[str]):
        self.key = key
        self.aliases = aliases

    def get_directory(self, tag: str) -> str:
        raise NotImplementedError()

    def install(self, tag: str, overwrite: bool) -> None:
        # Fallback to default tag if not provided
        tag = tag or config.get_dependency_tag(self.key)

        logger.debug(f"install: key={self.key}, tag={tag}")

        if self._should_skip(tag, overwrite):
            logger.debug("Already exists. Skip install.")
            return

        self.uninstall(tag)
        self._do_install(tag)

        # Upon installation we update the default tag
        config.set_dependency_tag(self.key, tag)
        self._post_install(tag)

    def _do_install(self, tag: str) -> None:
        raise NotImplementedError()

    def _post_install(self, tag: str):
        pass

    def _should_skip(self, tag: str, overwrite: bool) -> bool:
        if overwrite:
            return False
        return self.is_installed(tag)

    def uninstall(self, tag: str) -> None:
        raise NotImplementedError()

    def is_installed(self, tag: str) -> bool:
        raise NotImplementedError()

    def get_env(self) -> Dict[str, str]:
        raise NotImplementedError()


class StandaloneModule(DependencyModule):
    def __init__(self, key: str, aliases: List[str]):
        super().__init__(key, aliases)

    def _do_install(self, tag: str):
        self._download(tag)
        self._extract(tag)

    def uninstall(self, tag: str):
        if os.path.isdir(self.get_directory(tag)):
            shutil.rmtree(self.get_directory(tag))

    def is_installed(self, tag: str):
        return path.isdir(self.get_directory(tag))

    def _download(self, tag: str):
        url = self._get_download_url(tag)
        archive_path = self._get_archive_path(tag)
        downloader.download(url, archive_path)

    def _extract(self, tag: str):
        archive_path = self._get_archive_path(tag)
        destination_folder = self.get_directory(tag)
        utils.untar(archive_path, destination_folder)

    def get_directory(self, tag: str):
        folder = path.join(self.get_parent_directory(), tag)
        return folder

    def get_parent_directory(self):
        tools_folder = workstation.get_tools_folder()
        return path.join(tools_folder, self.key)

    def _get_download_url(self, tag: str) -> str:
        platform = workstation.get_platform()
        url = config.get_dependency_url(self.key, tag, platform)
        if url is None:
            raise errors.PlatformNotSupported(self.key, platform)

        url = url.replace("{TAG}", tag)
        return url

    def _get_archive_path(self, tag: str) -> str:
        tools_folder = workstation.get_tools_folder()
        archive = path.join(tools_folder, f"{self.key}.{tag}.tar.gz")
        return archive


class ArwenToolsModule(StandaloneModule):
    def __init__(self, key: str, aliases: List[str]):
        super().__init__(key, aliases)

    def _post_install(self, tag: str):
        directory = self.get_directory(tag)

        utils.mark_executable(path.join(directory, "arwen"))
        utils.mark_executable(path.join(directory, "arwendebug"))
        utils.mark_executable(path.join(directory, "test"))

        utils.symlink(path.join(directory, "arwendebug"), os.path.join(self.get_parent_directory(), "arwendebug"))
        utils.symlink(path.join(directory, "test"), os.path.join(self.get_parent_directory(), "mandos-test"))

    def get_env(self):
        return {
        }


class NodejsModule(StandaloneModule):
    def __init__(self, key: str, aliases: List[str]):
        super().__init__(key, aliases)

    def _post_install(self, tag: str):
        pass

    def get_env(self):
        return {
        }


class Rust(DependencyModule):
    def __init__(self, key: str, aliases: List[str]):
        super().__init__(key, aliases)

    def _do_install(self, tag: str) -> None:
        rustup_path = self._get_rustup_path()
        downloader.download("https://sh.rustup.rs", rustup_path)
        utils.mark_executable(rustup_path)

        args = [rustup_path, "--verbose", "--default-toolchain", "nightly", "--profile",
                "minimal", "--target", "wasm32-unknown-unknown", "--no-modify-path", "-y"]
        myprocess.run_process_async(args, env=self.get_env())

    def uninstall(self, tag: str):
        directory = self.get_directory("")
        if os.path.isdir(directory):
            shutil.rmtree(directory)

    def is_installed(self, tag: str):
        try:
            myprocess.run_process(["rustc", "--version"], env=self.get_env())
            return True
        except Exception:
            return False

    def _get_rustup_path(self):
        tools_folder = workstation.get_tools_folder()
        return path.join(tools_folder, "rustup.sh")

    def get_directory(self, tag: str):
        tools_folder = workstation.get_tools_folder()
        return path.join(tools_folder, "vendor-rust")

    def get_env(self):
        directory = self.get_directory("")

        return {
            "PATH": f"{path.join(directory, 'bin')}:{os.environ['PATH']}",
            "RUSTUP_HOME": directory,
            "CARGO_HOME": directory
        }
