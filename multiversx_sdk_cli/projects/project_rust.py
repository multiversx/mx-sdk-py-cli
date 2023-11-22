import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from multiversx_sdk_cli import dependencies, errors, utils, workstation
from multiversx_sdk_cli.constants import DEFAULT_CARGO_TARGET_DIR_NAME
from multiversx_sdk_cli.dependencies.modules import Rust
from multiversx_sdk_cli.projects.project_base import Project

logger = logging.getLogger("ProjectRust")


class ProjectRust(Project):
    def __init__(self, directory: Path):
        super().__init__(directory)

    def clean(self):
        env = self.get_env()

        args = [
            "sc-meta",
            "all",
            "clean",
            "--path",
            self.directory
        ]

        subprocess.check_call(args, env=env)

    def get_meta_folder(self):
        return self.path / 'meta'

    def get_wasm_view_folder(self):
        return self.path / 'wasm-view'

    def perform_build(self):
        meta = self.has_meta()
        if not meta:
            raise errors.NotSupportedProject("The project does not have a meta crate")

        self.run_meta()

    def prepare_build_wasm_args(self, args: List[str]):
        args.extend([
            "--target=wasm32-unknown-unknown",
            "--release",
            "--out-dir",
            self.get_output_folder()
        ])

    def run_meta(self):
        env = self.get_env()

        args = [
            "sc-meta",
            "all",
            "build"
        ]

        args.extend(self.forwarded_args)

        try:
            subprocess.check_call(args, env=env)
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(f"error code = {err.returncode}, see output")

    def _ensure_cargo_target_dir(self, target_dir: str):
        default_target_dir = str(workstation.get_tools_folder() / DEFAULT_CARGO_TARGET_DIR_NAME)
        target_dir = target_dir or default_target_dir
        utils.ensure_folder(target_dir)
        return target_dir

    def has_meta(self):
        return (self.get_meta_folder() / "Cargo.toml").exists()

    def has_wasm_view(self):
        return (self.get_wasm_view_folder() / "Cargo.toml").exists()

    def has_abi(self):
        return (self.get_abi_folder() / "Cargo.toml").exists()

    def get_abi_filepath(self):
        return self.get_abi_folder() / "abi.json"

    def get_abi_folder(self):
        return Path(self.directory, "abi")

    def _do_after_build_custom(self) -> List[Path]:
        outputs = [self.get_wasm_default_path()]
        if self.has_wasm_view():
            outputs.append(self.get_wasm_view_default_path())
        return outputs

    def get_dependencies(self):
        return ["rust"]

    def get_env(self):
        return dependencies.get_module_by_key("rust").get_env()

    def build_wasm_with_debug_symbols(self, build_options: Dict[str, Any]):
        rust_module = Rust("rust")
        rust_module.install(overwrite=False)

        cwd = self.path
        env = self.get_env()
        target_dir: str = build_options.get("target-dir", "")
        target_dir = self._ensure_cargo_target_dir(target_dir)

        args = [
            "sc-meta",
            "all",
            "build",
            "--wasm-symbols",
            "--wasm-suffix", "dbg",
            "--no-wasm-opt",
            "--target-dir", target_dir
        ]

        try:
            subprocess.check_call(args, env=env, cwd=cwd)
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(f"error code = {err.returncode}, see output")
