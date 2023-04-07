from enum import Enum
from pathlib import Path
from typing import Any, Dict, Tuple, Union

from multiversx_sdk_cli.errors import KnownError


class SoftwareResolution(Enum):
    RemoteArchives = "remote_archives"
    LocalSourceFolders = "local_source_folders"
    LocalPrebuiltCmdFolders = "local_prebuilt_cmd_folders"


class Software:
    def __init__(
            self,
            resolution: SoftwareResolution,
            remote_archives: 'SoftwareRemoteArchives',
            local_source_folders: 'SoftwareLocalSourceFolders',
            local_prebuilt_cmd_folders: 'SoftwareLocalPrebuiltCmdFolders'):
        self.resolution: SoftwareResolution = resolution
        self.remote_archives: SoftwareRemoteArchives = remote_archives
        self.local_source_folders: SoftwareLocalSourceFolders = local_source_folders
        self.local_prebuilt_cmd_folders: SoftwareLocalPrebuiltCmdFolders = local_prebuilt_cmd_folders

    def override(self, other: Dict[str, Any]):
        self.resolution = SoftwareResolution(other.get("resolution", self.resolution.value))
        self.remote_archives.override(other.get("remote_archives", dict()))
        self.local_source_folders.override(other.get("local_source_folders", dict()))
        self.local_prebuilt_cmd_folders.override(other.get("local_prebuilt_cmd_folders", dict()))

    def get_binaries_parents(self) -> Tuple[Path, Path, Path]:
        if self.resolution == SoftwareResolution.RemoteArchives:
            return (
                self.remote_archives.get_mx_chain_go_source_path() / "cmd" / "node",
                self.remote_archives.get_mx_chain_go_source_path() / "cmd" / "seednode",
                self.remote_archives.get_mx_chain_proxy_go_source_path() / "cmd" / "proxy",
            )
        elif self.resolution == SoftwareResolution.LocalSourceFolders:
            return (
                self.local_source_folders.ensure_mx_chain_go_path() / "cmd" / "node",
                self.local_source_folders.ensure_mx_chain_go_path() / "cmd" / "seednode",
                self.local_source_folders.ensure_mx_chain_proxy_go_path() / "cmd" / "proxy"
            )
        elif self.resolution == SoftwareResolution.LocalPrebuiltCmdFolders:
            return (
                self.local_prebuilt_cmd_folders.ensure_mx_chain_go_node_path(),
                self.local_prebuilt_cmd_folders.ensure_mx_chain_go_seednode_path(),
                self.local_prebuilt_cmd_folders.ensure_mx_chain_proxy_go_path()
            )

        raise KnownError(f"Software resolution {self.resolution} not supported")

    def get_node_config_folder(self):
        [node, _, _] = self.get_binaries_parents()
        return node / "config"

    def get_seednode_config_folder(self):
        [_, seednode, _] = self.get_binaries_parents()
        return seednode / "config"

    def get_proxy_config_folder(self):
        [_, _, proxy] = self.get_binaries_parents()
        return proxy / "config"

    def get_mx_chain_go_path_in_source(self, relative_path: Path) -> Path:
        if self.resolution == SoftwareResolution.RemoteArchives:
            return self.remote_archives.get_mx_chain_go_source_path() / relative_path
        elif self.resolution == SoftwareResolution.LocalSourceFolders:
            return self.local_source_folders.ensure_mx_chain_go_path() / relative_path
        elif self.resolution == SoftwareResolution.LocalPrebuiltCmdFolders:
            raise KnownError(f"Software resolution {self.resolution} does not support source code lookup")

        raise KnownError(f"Software resolution {self.resolution} not supported")


class SoftwareRemoteArchives:
    def __init__(self,
                 downloads_folder: Path,
                 mx_chain_go: str = "",
                 mx_chain_proxy_go: str = ""):
        self.downloads_folder: Path = downloads_folder.expanduser().resolve()
        self.mx_chain_go: str = mx_chain_go
        self.mx_chain_proxy_go: str = mx_chain_proxy_go

    def override(self, other: Dict[str, Any]):
        self.downloads_folder = Path(other.get("downloads_folder", self.downloads_folder)).expanduser().resolve()
        self.mx_chain_go = other.get("mx_chain_go", self.mx_chain_go)
        self.mx_chain_proxy_go = other.get("mx_chain_proxy_go", self.mx_chain_proxy_go)

    def ensure_mx_chain_go_url(self) -> str:
        return self._ensure_url("mx_chain_go", self.mx_chain_go)

    def ensure_mx_chain_proxy_go_url(self) -> str:
        return self._ensure_url("mx_chain_proxy_go", self.mx_chain_proxy_go)

    def _ensure_url(self, name: str, url: str) -> str:
        if not url:
            raise KnownError(f"URL {name} is not properly configured")
        return url

    def get_mx_chain_go_archive_path(self) -> Path:
        archive_suffix = Path(self.mx_chain_go).suffix
        return self.downloads_folder / f"mx_chain_go{archive_suffix}"

    def get_mx_chain_proxy_go_archive_path(self) -> Path:
        archive_suffix = Path(self.mx_chain_proxy_go).suffix
        return self.downloads_folder / f"mx_chain_proxy_go{archive_suffix}"

    def get_mx_chain_go_extract_path(self) -> Path:
        return self.downloads_folder / "mx_chain_go"

    def get_mx_chain_proxy_go_extract_path(self) -> Path:
        return self.downloads_folder / "mx_chain_proxy_go"

    def get_mx_chain_go_source_path(self) -> Path:
        extract_path = self.get_mx_chain_go_extract_path()
        # If has one subfolder, that one is the source code
        subfolders = list(extract_path.glob("*"))
        source_folder = subfolders[0] if len(subfolders) == 1 else extract_path
        # Heuristic to check if this is a valid source code folder
        assert (source_folder / "go.mod").exists(), f"This is not a valid source code folder: {source_folder}"
        return source_folder

    def get_mx_chain_proxy_go_source_path(self) -> Path:
        extract_path = self.get_mx_chain_proxy_go_extract_path()
        # If has one subfolder, that one is the source code
        subfolders = list(extract_path.glob("*"))
        source_folder = subfolders[0] if len(subfolders) == 1 else extract_path
        # Heuristic to check if this is a valid source code folder
        assert (source_folder / "go.mod").exists(), f"This is not a valid source code folder: {source_folder}"
        return source_folder


class SoftwareLocalSourceFolders:
    def __init__(self,
                 mx_chain_go: str = "",
                 mx_chain_proxy_go: str = ""):
        self.mx_chain_go: str = mx_chain_go
        self.mx_chain_proxy_go: str = mx_chain_proxy_go

    def override(self, other: Dict[str, Any]):
        self.mx_chain_go = other.get("mx_chain_go", self.mx_chain_go)
        self.mx_chain_proxy_go = other.get("mx_chain_proxy_go", self.mx_chain_proxy_go)

    def ensure_mx_chain_go_path(self) -> Path:
        return self._ensure_path("mx_chain_go", self.mx_chain_go)

    def ensure_mx_chain_proxy_go_path(self) -> Path:
        return self._ensure_path("mx_chain_proxy_go", self.mx_chain_proxy_go)

    def _ensure_path(self, name: str, path_value: str) -> Path:
        if not path_value:
            raise KnownError(f"{name} is not properly configured")

        path = Path(path_value).expanduser().resolve()

        if not path.is_dir():
            raise KnownError(f"{name} path is not a directory: {path}")

        return path


class SoftwareLocalPrebuiltCmdFolders:
    def __init__(self,
                 mx_chain_go_node: str = "",
                 mx_chain_go_seednode: str = "",
                 mx_chain_proxy_go: str = ""):
        self.mx_chain_go_node: str = mx_chain_go_node
        self.mx_chain_go_seednode: str = mx_chain_go_seednode
        self.mx_chain_proxy_go: str = mx_chain_proxy_go

    def override(self, other: Dict[str, Any]):
        self.mx_chain_go_node = other.get("mx_chain_go_node", self.mx_chain_go_node)
        self.mx_chain_go_seednode = other.get("mx_chain_go_seednode", self.mx_chain_go_seednode)
        self.mx_chain_proxy_go = other.get("mx_chain_proxy_go", self.mx_chain_proxy_go)

    def ensure_mx_chain_go_node_path(self) -> Path:
        return self._ensure_path("mx_chain_go_node", self.mx_chain_go_node)

    def ensure_mx_chain_go_seednode_path(self) -> Path:
        return self._ensure_path("mx_chain_go_seednode", self.mx_chain_go_seednode)

    def ensure_mx_chain_proxy_go_path(self) -> Path:
        return self._ensure_path("mx_chain_proxy_go", self.mx_chain_proxy_go)

    def ensure_mx_chain_go_node_config_path(self) -> Path:
        return self._ensure_path("mx_chain_go_node_config", self.ensure_mx_chain_go_node_path() / "config")

    def ensure_mx_chain_go_seednode_config_path(self) -> Path:
        return self._ensure_path("mx_chain_go_seednode_config", self.ensure_mx_chain_go_seednode_path() / "config")

    def ensure_mx_chain_proxy_go_config_path(self) -> Path:
        return self._ensure_path("mx_chain_proxy_go_config", self.ensure_mx_chain_proxy_go_path() / "config")

    def _ensure_path(self, name: str, path_value: Union[str, Path]) -> Path:
        if not path_value:
            raise KnownError(f"{name} is not properly configured")

        path = Path(path_value).expanduser().resolve()

        if not path.is_dir():
            raise KnownError(f"{name} path is not a directory: {path}")

        return path
