from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from multiversx_sdk_cli.errors import KnownError
from multiversx_sdk_cli.localnet.config_part import ConfigPart


class SoftwareResolution(Enum):
    Remote = "remote"
    Local = "local"


class Software(ConfigPart):
    def __init__(
            self,
            mx_chain_go: 'SoftwareChainGo',
            mx_chain_proxy_go: 'SoftwareChainProxyGo'):
        self.mx_chain_go = mx_chain_go
        self.mx_chain_proxy_go = mx_chain_proxy_go

    def get_name(self) -> str:
        return "software"

    def _do_override(self, other: Dict[str, Any]):
        self.mx_chain_go.override(other.get("mx_chain_go", {}))
        self.mx_chain_proxy_go.override(other.get("mx_chain_proxy_go", {}))


class SoftwareChainGo(ConfigPart):
    def __init__(self,
                 resolution: SoftwareResolution,
                 archive_url: str,
                 archive_download_folder: Path,
                 archive_extraction_folder: Path,
                 local_path: Optional[Path]):
        self.resolution: SoftwareResolution = resolution
        self.archive_url: str = archive_url
        self.archive_download_folder: Path = archive_download_folder
        self.archive_extraction_folder: Path = archive_extraction_folder
        self.local_path: Optional[Path] = local_path
        self._verify()

    def get_name(self) -> str:
        return "mx_chain_go"

    def _do_override(self, other: Dict[str, Any]) -> None:
        self.resolution = SoftwareResolution(other.get("resolution", self.resolution))
        self.archive_url = other.get("archive_url", self.archive_url)
        self.archive_download_folder = other.get("archive_download_folder", self.archive_download_folder)
        self.archive_extraction_folder = other.get("archive_extraction_folder", self.archive_extraction_folder)
        self.local_path = other.get("local_path", self.local_path)
        self._verify()

    def _verify(self):
        if self.resolution == SoftwareResolution.Remote:
            if not self.archive_url:
                raise KnownError(f"Resolution is {self.resolution}, but configuration section {self.get_name()} has no 'archive_url'")
        if self.resolution == SoftwareResolution.Local:
            if not self.local_path:
                raise KnownError(f"Resolution is {self.resolution}, but configuration section {self.get_name()} has no 'local_path'")
            folder_must_exist(self.local_path)

    def get_path_within_source(self, relative_path: Path) -> Path:
        return self.get_source_folder() / relative_path

    def get_source_folder(self) -> Path:
        if self.resolution == SoftwareResolution.Remote:
            return self._locate_source_folder_in_archive_extraction_folder()
        if self.resolution == SoftwareResolution.Local:
            assert self.local_path
            return self.local_path

        raise KnownError(f"Unknown resolution: {self.resolution}")

    def _locate_source_folder_in_archive_extraction_folder(self) -> Path:
        # If has one subfolder, that one is the source code
        subfolders = list(self.archive_extraction_folder.glob("*"))
        source_folder = subfolders[0] if len(subfolders) == 1 else self.archive_extraction_folder
        # Heuristic to check if this is a valid source code folder
        assert (source_folder / "go.mod").exists(), f"This is not a valid source code folder: {source_folder}"
        return source_folder

    def get_cmd_node_folder(self):
        folder = self._get_cmd_folder() / "node"
        folder_must_exist(folder)
        return folder

    def get_cmd_seednode_folder(self):
        folder = self._get_cmd_folder() / "seednode"
        folder_must_exist(folder)
        return folder

    def _get_cmd_folder(self):
        folder = self.get_path_within_source(Path("cmd"))
        folder_must_exist(folder)
        return folder

    def is_node_built(self):
        return (self.get_cmd_node_folder() / "node").exists()

    def is_seednode_built(self):
        return (self.get_cmd_seednode_folder() / "seednode").exists()

    def get_node_config_folder(self):
        return self.get_cmd_node_folder() / "config"

    def get_seednode_config_folder(self):
        return self.get_cmd_seednode_folder() / "config"

    def node_config_must_exist(self):
        folder_must_exist(self.get_node_config_folder())

    def seednode_config_must_exist(self):
        folder_must_exist(self.get_seednode_config_folder())


class SoftwareChainProxyGo(ConfigPart):
    def __init__(self,
                 resolution: SoftwareResolution,
                 archive_url: str,
                 archive_download_folder: Path,
                 archive_extraction_folder: Path,
                 local_path: Optional[Path]):
        self.resolution: SoftwareResolution = resolution
        self.archive_url: str = archive_url
        self.archive_download_folder: Path = archive_download_folder
        self.archive_extraction_folder: Path = archive_extraction_folder
        self.local_path: Optional[Path] = local_path
        self._verify()

    def get_name(self) -> str:
        return "mx_chain_proxy_go"

    def _do_override(self, other: Dict[str, Any]) -> None:
        self.resolution = SoftwareResolution(other.get("resolution", self.resolution))
        self.archive_url = other.get("archive_url", self.archive_url)
        self.archive_download_folder = other.get("archive_download_folder", self.archive_download_folder)
        self.archive_extraction_folder = other.get("archive_extraction_folder", self.archive_extraction_folder)
        self.local_path = other.get("local_path", self.local_path)
        self._verify()

    def _verify(self):
        if self.resolution == SoftwareResolution.Remote:
            if not self.archive_url:
                raise KnownError(f"Resolution is {self.resolution}, but configuration section {self.get_name()} has no 'archive_url'")
        if self.resolution == SoftwareResolution.Local:
            if not self.local_path:
                raise KnownError(f"Resolution is {self.resolution}, but configuration section {self.get_name()} has no 'local_path'")
            folder_must_exist(self.local_path)

    def get_path_within_source(self, relative_path: Path) -> Path:
        return self.get_source_folder() / relative_path

    def get_source_folder(self) -> Path:
        if self.resolution == SoftwareResolution.Remote:
            return self._locate_source_folder_in_archive_extraction_folder()
        if self.resolution == SoftwareResolution.Local:
            assert self.local_path
            return self.local_path

        raise KnownError(f"Unknown resolution: {self.resolution}")

    def _locate_source_folder_in_archive_extraction_folder(self) -> Path:
        # If has one subfolder, that one is the source code
        subfolders = list(self.archive_extraction_folder.glob("*"))
        source_folder = subfolders[0] if len(subfolders) == 1 else self.archive_extraction_folder
        # Heuristic to check if this is a valid source code folder
        assert (source_folder / "go.mod").exists(), f"This is not a valid source code folder: {source_folder}"
        return source_folder

    def get_cmd_proxy_folder(self):
        folder = self._get_cmd_folder() / "proxy"
        folder_must_exist(folder)
        return folder

    def _get_cmd_folder(self):
        folder = self.get_path_within_source(Path("cmd"))
        folder_must_exist(folder)
        return folder

    def is_proxy_built(self):
        return (self.get_cmd_proxy_folder() / "proxy").exists()

    def get_proxy_config_folder(self):
        return self.get_cmd_proxy_folder() / "config"

    def proxy_config_must_exist(self):
        folder_must_exist(self.get_proxy_config_folder())


def folder_must_exist(path: Path) -> None:
    if not path.exists():
        raise KnownError(f"Folder does not exist: {path}")


def file_must_exist(path: Path) -> None:
    if not path.exists():
        raise KnownError(f"File does not exist: {path}")
