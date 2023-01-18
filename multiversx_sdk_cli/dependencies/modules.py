import logging
import os
import shutil
from os import path
from pathlib import Path
from typing import Dict, List, Optional

from multiversx_sdk_cli import (config, dependencies, downloader, errors, myprocess, utils,
                   workstation)

logger = logging.getLogger("modules")


class DependencyModule:
    def __init__(self, key: str, aliases: List[str]):
        self.key = key
        self.aliases = aliases

    def get_directory(self, tag: str) -> Path:
        raise NotImplementedError()

    def install(self, tag: str, overwrite: bool) -> None:
        # Fallback to default tag if not provided
        tag = tag or config.get_dependency_tag(self.key)

        if tag == 'latest':
            tag = self.get_latest_release()

        logger.debug(f"install: key={self.key}, tag={tag}")

        if self._should_skip(tag, overwrite):
            logger.debug("Already exists. Skip install.")
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

    def get_env(self) -> Dict[str, str]:
        raise NotImplementedError()

    def get_latest_release(self) -> str:
        raise NotImplementedError()


class StandaloneModule(DependencyModule):
    def __init__(self,
                 key: str,
                 aliases: List[str] = None,
                 repo_name: Optional[str] = None,
                 organisation: Optional[str] = None):
        if aliases is None:
            aliases = list()

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

    def get_source_directory(self, tag: str):
        # Due to how the GitHub creates archives for repository releases, the
        # path will contain the tag in two variants: with the 'v' prefix (e.g.
        # "v1.1.0"), but also without (e.g. "1.1.0"), hence the need to remove
        # the initial 'v'.
        tag_no_v = tag
        if tag_no_v.startswith("v"):
            tag_no_v = tag_no_v[1:]
        assert isinstance(self.repo_name, str)
        source_folder = self.get_directory(tag) / f'{self.repo_name}-{tag_no_v}'
        return source_folder

    def get_parent_directory(self) -> Path:
        return config.get_dependency_parent_directory(self.key)

    def _get_download_url(self, tag: str) -> str:
        platform = workstation.get_platform()

        url = config.get_dependency_url(self.key, tag, platform)
        if url is None:
            raise errors.PlatformNotSupported(self.key, platform)

        url = url.replace("{TAG}", tag)
        return url

    def get_latest_release(self) -> str:
        if self.repo_name is None or self.organisation is None:
            raise ValueError(f'{self.key}: repo_name or organisation not specified')

        org_repo = f'{self.organisation}/{self.repo_name}'
        tag = utils.query_latest_release_tag(org_repo)
        return tag

    def _get_archive_path(self, tag: str) -> Path:
        tools_folder = Path(workstation.get_tools_folder())
        archive = tools_folder / f"{self.key}.{tag}.{self.archive_type}"
        return archive


class VMToolsModule(StandaloneModule):
    def __init__(self, key: str, aliases: List[str] = None):
        if aliases is None:
            aliases = list()

        super().__init__(key, aliases)
        self.repo_name = 'mx-chain-vm-go'
        self.organisation = 'multiversx'

    def _post_install(self, tag: str):
        dependencies.install_module('golang')

        self.build_binary(tag, 'test')
        self.make_binary_symlink_in_parent_folder(tag, 'test', 'run-scenarios')
        self.copy_libwasmer_in_parent_directory(tag)

    def build_binary(self, tag: str, binary_name: str):
        source_folder = self.binary_source_folder(tag, binary_name)
        golang = dependencies.get_module_by_key("golang")
        golang_env = golang.get_env()
        myprocess.run_process(['go', 'build'], cwd=source_folder, env=golang_env)

    def binary_source_folder(self, tag: str, binary_name: str):
        directory = self.get_source_directory(tag)
        return directory / 'cmd' / binary_name

    def make_binary_symlink_in_parent_folder(self, tag: str, binary_name: str, symlink_name: str):
        source_folder = self.binary_source_folder(tag, binary_name)
        binary = source_folder / binary_name

        parent = self.get_parent_directory()
        symlink = parent / symlink_name

        symlink.unlink(missing_ok=True)
        symlink.symlink_to(binary)

    def copy_libwasmer_in_parent_directory(self, tag: str):
        libwasmer_directory = self.get_source_directory(tag) / 'wasmer'
        cmd_test_directory = self.get_source_directory(tag) / 'cmd' / 'test'
        parent_directory = self.get_parent_directory()
        for f in libwasmer_directory.iterdir():
            if f.suffix in ['.dylib', '.so', '.dll']:
                # Copy the dynamic library near the "run-scenarios" symlink
                shutil.copy(f, parent_directory)
                # Though, also copy the dynamic library near the target executable (seems to be necessary on MacOS)
                shutil.copy(f, cmd_test_directory)

    def get_env(self) -> Dict[str, str]:
        return dict()


class GolangModule(StandaloneModule):
    def __init__(self, key: str, aliases: List[str] = None):
        if aliases is None:
            aliases = list()

        super().__init__(key, aliases)

    def _post_install(self, tag: str):
        parent_directory = self.get_parent_directory()
        utils.ensure_folder(path.join(parent_directory, "GOPATH"))
        utils.ensure_folder(path.join(parent_directory, "GOCACHE"))

    def get_env(self):
        directory = self.get_directory(config.get_dependency_tag(self.key))
        parent_directory = self.get_parent_directory()

        return {
            "PATH": f"{path.join(directory, 'go/bin')}:{os.environ['PATH']}",
            "GOPATH": self.get_gopath(),
            "GOCACHE": path.join(parent_directory, "GOCACHE"),
            "GOROOT": path.join(directory, "go")
        }

    def get_gopath(self):
        return path.join(self.get_parent_directory(), "GOPATH")

    def get_latest_release(self) -> str:
        raise errors.UnsupportedConfigurationValue("Golang tag must always be explicit, not latest")


class NodejsModule(StandaloneModule):
    def __init__(self, key: str, aliases: List[str]):
        super().__init__(key, aliases)

    def _post_install(self, tag: str):
        # We'll create a symlink towards the payload folder
        subfolder_to_bypass = self._get_download_url(tag).split("/")[-1]
        subfolder_to_bypass = subfolder_to_bypass.replace(f".{self.archive_type}", "")
        payload_folder = path.join(self.get_directory(tag), subfolder_to_bypass)
        link = path.join(self.get_parent_directory(), "latest")

        utils.symlink(payload_folder, link)

    def get_env(self):
        bin_folder = path.join(self.get_parent_directory(), "latest", "bin")

        return {
            "PATH": f"{bin_folder}:{os.environ['PATH']}",
        }

    def get_latest_release(self) -> str:
        raise errors.UnsupportedConfigurationValue("Nodejs tag must always be explicit, not latest")


class NpmModule(DependencyModule):
    def __init__(self, key: str, aliases: List[str] = []):
        super().__init__(key, aliases)

    def get_nodejs(self) -> DependencyModule:
        return dependencies.get_module_by_key("nodejs")

    def get_nodejs_env(self) -> Dict[str, str]:
        return self.get_nodejs().get_env()

    def _do_install(self, tag: str) -> None:
        args = ["npm", "install", f"{self.key}@{tag}", "-g"]
        myprocess.run_process(args, env=self.get_nodejs_env())

    def uninstall(self, tag: str) -> None:
        args = ["npm", "uninstall", self.key, "-g"]
        myprocess.run_process(args, env=self.get_nodejs_env())

    def get_env(self):
        bin_folder = config.get_dependency_parent_directory("nodejs") / "latest" / "lib" / "node_modules" / self.key / "bin"

        return {
            "PATH": f"{bin_folder}:{os.environ['PATH']}",
        }

    def is_installed(self, tag: str) -> bool:
        try:
            myprocess.run_process(["wasm-opt", "--version"], env=self.get_env())
            return True
        except FileNotFoundError:
            return False

    def get_latest_release(self) -> str:
        return "latest"


class Rust(DependencyModule):
    def __init__(self, key: str, aliases: List[str] = None):
        if aliases is None:
            aliases = list()

        super().__init__(key, aliases)

    def _do_install(self, tag: str) -> None:
        rustup_path = self._get_rustup_path()
        downloader.download("https://sh.rustup.rs", rustup_path)
        utils.mark_executable(rustup_path)
        if tag:
            toolchain = tag
        else:
            toolchain = "nightly"

        args = [rustup_path, "--verbose", "--default-toolchain", toolchain, "--profile",
                "minimal", "--target", "wasm32-unknown-unknown", "--no-modify-path", "-y"]
        myprocess.run_process(args, env=self.get_env_for_install())

    def uninstall(self, tag: str):
        directory = self.get_directory("")
        if os.path.isdir(directory):
            shutil.rmtree(directory)

    def is_installed(self, tag: str) -> bool:
        try:
            myprocess.run_process(["rustc", "--version"], env=self.get_env_for_is_installed())
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
            # At this moment, cc (build-essential) is sometimes required by the meta crate (e.g. for reports)
            "PATH": f"{path.join(directory, 'bin')}:{os.environ['PATH']}",
            "RUSTUP_HOME": directory,
            "CARGO_HOME": directory
        }

    def get_env_for_is_installed(self):
        directory = self.get_directory("")

        return {
            # Here, we do not include the system PATH
            "PATH": f"{path.join(directory, 'bin')}",
            "RUSTUP_HOME": directory,
            "CARGO_HOME": directory
        }

    def get_env_for_install(self):
        directory = self.get_directory("")

        return {
            # For installation, wget (or curl) and cc (build-essential) are also required.
            "PATH": f"{path.join(directory, 'bin')}:{os.environ['PATH']}",
            "RUSTUP_HOME": directory,
            "CARGO_HOME": directory
        }

    def get_latest_release(self) -> str:
        raise errors.UnsupportedConfigurationValue("Rust tag must either be explicit, empty or 'nightly'")


class CargoModule(DependencyModule):
    def __init__(self, key: str, aliases: List[str] = None):
        if aliases is None:
            aliases = list()

        super().__init__(key, aliases)

    def _do_install(self, tag: str) -> None:
        self._run_command_with_rust_env(["cargo", "install", self.key])

    def is_installed(self, tag: str) -> bool:
        rust = dependencies.get_module_by_key("rust")
        output = myprocess.run_process(["cargo", "install", "--list"], rust.get_env())
        for line in output.splitlines():
            if self.key == line.strip():
                return True
        return False

    def uninstall(self, tag: str):
        if self.is_installed(tag):
            self._run_command_with_rust_env(["cargo", "uninstall", self.key])

    def get_latest_release(self) -> str:
        return "latest"

    def _run_command_with_rust_env(self, args: List[str]) -> str:
        rust = dependencies.get_module_by_key("rust")
        return myprocess.run_process(args, rust.get_env())


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
