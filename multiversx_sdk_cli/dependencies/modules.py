import logging
import os
import shutil
from os import path
from pathlib import Path
from typing import Optional

from multiversx_sdk_cli import config, downloader, errors, utils, workstation
from multiversx_sdk_cli.dependencies.resolution import (
    DependencyResolution,
    get_dependency_resolution,
)

logger = logging.getLogger("modules")


class DependencyModule:
    def __init__(self, key: str, aliases: list[str] = []):
        self.key = key
        self.aliases = aliases

    def get_directory(self, tag: str) -> Path:
        raise NotImplementedError()

    def install(self, overwrite: bool) -> None:
        # We install the default tag
        tag = config.get_dependency_tag(self.key)

        logger.info(f"install: key={self.key}, tag={tag}, overwrite={overwrite}")

        if self._should_skip(tag, overwrite):
            logger.info("Already exists. Skip install.")
            return

        self.uninstall(tag)
        self._do_install(tag)

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

    def get_env(self) -> dict[str, str]:
        raise NotImplementedError()

    def get_resolution(self) -> DependencyResolution:
        return get_dependency_resolution(self.key)


class StandaloneModule(DependencyModule):
    def __init__(
        self,
        key: str,
        aliases: list[str] = [],
        repo_name: Optional[str] = None,
        organisation: Optional[str] = None,
    ):
        super().__init__(key, aliases)
        self.archive_type = "tar.gz"
        self.repo_name = repo_name
        self.organisation = organisation

    def _do_install(self, tag: str):
        self._download(tag)
        self._extract(tag)

    def uninstall(self, tag: str):
        if os.path.isdir(self.get_directory(tag)):
            shutil.rmtree(self.get_directory(tag))

    def is_installed(self, tag: str) -> bool:
        return path.isdir(self.get_directory(tag))

    def _download(self, tag: str):
        url = self._get_download_url(tag)
        archive_path = self._get_archive_path(tag)
        downloader.download(url, str(archive_path))

    def _extract(self, tag: str):
        archive_path = self._get_archive_path(tag)
        destination_folder = self.get_directory(tag)

        if self.archive_type == "tar.gz":
            utils.untar(archive_path, destination_folder)
        elif self.archive_type == "zip":
            utils.unzip(archive_path, destination_folder)
        else:
            raise errors.UnknownArchiveType(self.archive_type)

    def get_directory(self, tag: str) -> Path:
        return config.get_dependency_directory(self.key, tag)

    def get_source_directory(self, tag: str) -> Path:
        # Due to how the GitHub creates archives for repository releases, the
        # path will contain the tag in two variants: with the 'v' prefix (e.g.
        # "v1.1.0"), but also without (e.g. "1.1.0"), hence the need to remove
        # the initial 'v'.
        tag_no_v = tag
        if tag_no_v.startswith("v"):
            tag_no_v = tag_no_v[1:]
        assert isinstance(self.repo_name, str)

        source_folder_option_1 = self.get_directory(tag) / f"{self.repo_name}-{tag_no_v}"
        source_folder_option_2 = self.get_directory(tag) / f"{self.repo_name}-{tag}"
        return source_folder_option_1 if source_folder_option_1.exists() else source_folder_option_2

    def get_parent_directory(self) -> Path:
        return config.get_dependency_parent_directory(self.key)

    def _get_download_url(self, tag: str) -> str:
        platform = workstation.get_platform()

        url = config.get_dependency_url(self.key, tag, platform)
        if not url:
            raise errors.PlatformNotSupported(self.key, platform)

        url = url.replace("{TAG}", tag)
        return url

    def _get_archive_path(self, tag: str) -> Path:
        tools_folder = Path(workstation.get_tools_folder())
        archive = tools_folder / f"{self.key}.{tag}.{self.archive_type}"
        return archive


class GolangModule(StandaloneModule):
    def _post_install(self, tag: str):
        parent_directory = self.get_parent_directory()
        utils.ensure_folder(path.join(parent_directory, "GOPATH"))
        utils.ensure_folder(path.join(parent_directory, "GOCACHE"))

    def is_installed(self, tag: str) -> bool:
        resolution = self.get_resolution()

        if resolution == DependencyResolution.Host:
            which_go = shutil.which("go")
            logger.info(f"which go: {which_go}")

            return which_go is not None
        if resolution == DependencyResolution.SDK:
            return super().is_installed(tag)

        raise errors.BadDependencyResolution(self.key, resolution)

    def get_env(self) -> dict[str, str]:
        resolution = self.get_resolution()
        directory = self.get_directory(config.get_dependency_tag(self.key))
        parent_directory = self.get_parent_directory()

        if resolution == DependencyResolution.Host:
            return {
                "PATH": os.environ.get("PATH", ""),
                "GOPATH": os.environ.get("GOPATH", ""),
                "GOCACHE": os.environ.get("GOCACHE", ""),
                "GOROOT": os.environ.get("GOROOT", ""),
            }
        if resolution == DependencyResolution.SDK:
            current_path = os.environ.get("PATH", "")
            current_path_parts = current_path.split(":")
            current_path_parts_without_go = [part for part in current_path_parts if "/go/bin" not in part]
            current_path_without_go = ":".join(current_path_parts_without_go)

            return {
                # At this moment, cc (build-essential) is needed to compile go dependencies (e.g. Node, VM)
                "PATH": f"{(directory / 'go' / 'bin')}:{current_path_without_go}",
                "GOPATH": str(self.get_gopath()),
                "GOCACHE": str(parent_directory / "GOCACHE"),
                "GOROOT": str(directory / "go"),
            }

        raise errors.BadDependencyResolution(self.key, resolution)

    def get_gopath(self) -> Path:
        return self.get_parent_directory() / "GOPATH"


class TestWalletsModule(StandaloneModule):
    def __init__(self, key: str):
        super().__init__(key, [])
        self.organisation = "multiversx"
        self.repo_name = "mx-sdk-testwallets"

    def _post_install(self, tag: str):
        # We'll create a "latest" symlink
        target = self.get_source_directory(tag)
        link = path.join(self.get_parent_directory(), "latest")
        utils.symlink(str(target), link)
