import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Set, cast

from multiversx_sdk_cli import dependencies, errors, utils, workstation
from multiversx_sdk_cli.constants import DEFAULT_CARGO_TARGET_DIR_NAME
from multiversx_sdk_cli.projects.project_base import Project

logger = logging.getLogger("ProjectRust")


class ProjectRust(Project):
    def __init__(self, directory: Path):
        super().__init__(directory)
        self.cargo_file = self.get_cargo_file()

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

    def get_cargo_file(self):
        cargo_path = self.path / 'Cargo.toml'
        return CargoFile(cargo_path)

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

    def check_if_sc_meta_is_installed(self):
        which_sc_meta = shutil.which("sc-meta")

        if which_sc_meta is None:
            raise errors.KnownError("'sc-meta' is not installed. Run 'cargo install multiversx-sc-meta' then try again.")

    def run_meta(self):
        self.check_if_sc_meta_is_installed()
        env = self.get_env()

        with_wasm_opt = not self.options.get("no-wasm-opt")
        if with_wasm_opt:
            check_wasm_opt_installed()
            wasm_opt = dependencies.get_module_by_key("wasm-opt")
            env = merge_env(env, wasm_opt.get_env())

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

    def get_wasm_default_name(self, suffix: str = "") -> str:
        return f"{self.cargo_file.package_name}{suffix}.wasm"

    def _do_after_build_custom(self) -> List[Path]:
        if not self.has_meta():
            base_name = str(self.cargo_file.package_name)
            temporary_wasm_base_name = base_name.replace("-", "_")
            wasm_file = self.get_wasm_path(f"{temporary_wasm_base_name}_wasm.wasm")
            wasm_file.rename(self.get_wasm_default_path())

            if self.has_abi():
                abi_file = self.get_abi_filepath()
                abi_file_renamed = Path(self.get_output_folder(), f"{base_name}.abi.json")
                abi_file.rename(abi_file_renamed)

        outputs = [self.get_wasm_default_path()]
        if self.has_wasm_view():
            outputs.append(self.get_wasm_view_default_path())
        return outputs

    def get_dependencies(self):
        return ["rust"]

    def get_env(self):
        return dependencies.get_module_by_key("rust").get_env()

    def build_wasm_with_debug_symbols(self, build_options: Dict[str, Any]):
        self.check_if_sc_meta_is_installed()

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


class CargoFile:
    data: Dict[str, Any]

    def __init__(self, path: Path):
        self.data = {}
        self.path = path

        try:
            self._parse_file()
        except Exception as err:
            raise errors.BuildError("Can't read or parse [Cargo.toml] file", err)

    def _parse_file(self):
        self.data = utils.read_toml_file(self.path)

    @property
    def package_name(self):
        return self._get_package().get("name")

    @package_name.setter
    def package_name(self, value):
        self._get_package().update({"name": value})

    @property
    def version(self):
        return self._get_package().get("version")

    @version.setter
    def version(self, value):
        self._get_package().update({"version": value})

    @property
    def authors(self):
        return self._get_package().get("authors")

    @authors.setter
    def authors(self, value):
        self._get_package().update({"authors": value})

    @property
    def edition(self):
        return self._get_package().get("edition")

    @edition.setter
    def edition(self, value):
        self._get_package().update({"edition": value})

    @property
    def publish(self):
        return self._get_package().get("publish")

    @publish.setter
    def publish(self, value):
        self._get_package().update({"publish": value})

    def save(self):
        utils.write_toml_file(self.path, self.data)

    def _get_package(self) -> Dict[str, Any]:
        if "package" not in self.data:
            self.data["package"] = {}
        package = cast(Dict[str, Any], self.data['package'])
        return package

    def get_dependencies(self) -> Dict[str, Any]:
        if "dependencies" not in self.data:
            self.data["dependencies"] = {}
        dependencies = cast(Dict[str, Any], self.data['dependencies'])
        return dependencies

    def get_dev_dependencies(self) -> Dict[str, Any]:
        if "dev-dependencies" not in self.data:
            self.data["dev-dependencies"] = {}
        dev_dependencies = cast(Dict[str, Any], self.data['dev-dependencies'])
        return dev_dependencies

    def get_dependency(self, name: str) -> Dict[str, Any]:
        dependencies = self.get_dependencies()
        dependency = cast(Dict[str, Any], dependencies.get(name))
        if dependency is None:
            raise errors.BuildError(f"Can't get cargo dependency: {name}")
        return dependency

    def get_dev_dependency(self, name) -> Dict[str, Any]:
        dependencies = self.get_dev_dependencies()
        dependency = cast(Dict[str, Any], dependencies.get(name))
        if dependency is None:
            raise errors.BuildError(f"Can't get cargo dev-dependency: {name}")
        return dependency


def paths_of(env: Dict[str, str], key: str) -> Set[str]:
    try:
        return set(env[key].split(":"))
    except KeyError:
        return set()


def merge_env(first: Dict[str, str], second: Dict[str, str]) -> Dict[str, str]:
    """
>>> merge_env({'PATH':'first:common', 'CARGO_PATH': 'cargo_path'}, {'PATH':'second:common', 'EXAMPLE': 'other'})
{'CARGO_PATH': 'cargo_path', 'EXAMPLE': 'other', 'PATH': 'common:first:second'}
    """
    keys = set(first.keys()).union(second.keys())
    merged: Dict[str, str] = dict()
    for key in sorted(keys):
        values = paths_of(first, key).union(paths_of(second, key))
        merged[key] = ":".join(sorted(values))
    return merged


def check_wasm_opt_installed() -> None:
    wasm_opt = dependencies.get_module_by_key("wasm-opt")
    if not wasm_opt.is_installed(""):
        logger.warn("""
    Skipping optimization because wasm-opt is not installed.

    To install it run:
        mxpy deps install wasm-opt

    Alternatively, pass the "--no-wasm-opt" argument in order to skip the optimization step.
        """)
    else:
        logger.info("wasm-opt is installed.")
