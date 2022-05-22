import logging
import subprocess
from os import path
from pathlib import Path
from typing import Any, Dict, List, Set, cast

from erdpy import dependencies, errors, myprocess, utils
from erdpy import workstation
from erdpy.constants import DEFAULT_CARGO_TARGET_DIR_NAME
from erdpy.projects.project_base import Project

logger = logging.getLogger("ProjectRust")


class ProjectRust(Project):
    def __init__(self, directory: Path):
        super().__init__(directory)
        self.cargo_file = self.get_cargo_file()

    def clean(self):
        super().clean()
        utils.remove_folder(path.join(self.directory, "wasm", "target"))
        utils.remove_folder(path.join(self.directory, "meta", "target"))

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

        try:
            # The meta crate handles the build process, ABI generation and
            # allows contract developers to add extra
            # preparation steps before building.
            self.run_meta()
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def prepare_build_wasm_args(self, args: List[str]):
        args.extend([
            "--target=wasm32-unknown-unknown",
            "--release",
            "--out-dir",
            self.get_output_folder()
        ])

    def run_meta(self):
        cwd = self.get_meta_folder()
        env = self.get_env()

        with_wasm_opt = not self.options.get("no-wasm-opt")
        if with_wasm_opt:
            check_wasm_opt_installed()
            wasm_opt = dependencies.get_module_by_key("wasm-opt")
            env = merge_env(env, wasm_opt.get_env())

        # run the meta executable with the arguments `build --target=...`
        args = [
            "cargo",
            "run",
            "build",
        ]

        self.prepare_build_wasm_args(args)
        self.decorate_cargo_args(args)

        return_code = myprocess.run_process_async(args, env=env, cwd=str(cwd))
        if return_code != 0:
            raise errors.BuildError(f"error code = {return_code}, see output")

    def decorate_cargo_args(self, args: List[str]):
        target_dir: str = self.options.get("cargo-target-dir", "")
        target_dir = self._ensure_cargo_target_dir(target_dir)
        no_wasm_opt = self.options.get("no-wasm-opt")
        wasm_symbols = self.options.get("wasm-symbols")
        wasm_name = self.options.get("wasm-name")
        wasm_suffix = self.options.get("wasm-suffix")

        args.extend(["--target-dir", target_dir])

        if no_wasm_opt:
            args.extend(["--no-wasm-opt"])
        if wasm_symbols:
            args.extend(["--wasm-symbols"])
        if wasm_name:
            args.extend(["--wasm-name", wasm_name])
        if wasm_suffix:
            args.extend(["--wasm-suffix", wasm_suffix])

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
        cwd = self.get_meta_folder()
        env = self.get_env()
        target_dir: str = build_options.get("cargo-target-dir", "")
        target_dir = self._ensure_cargo_target_dir(target_dir)

        args = [
            "cargo",
            "run",
            "build",
            "--wasm-symbols",
            "--wasm-suffix", "dbg",
            "--no-wasm-opt",
            "--target-dir", target_dir
        ]

        return_code = myprocess.run_process_async(args, env=env, cwd=str(cwd))
        if return_code != 0:
            raise errors.BuildError(f"error code = {return_code}, see output")


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


def merge_env(first: Dict[str, str], second: Dict[str, str]):
    """
>>> merge_env({'PATH':'first:common', 'CARGO_PATH': 'cargo_path'}, {'PATH':'second:common', 'EXAMPLE': 'other'})
{'CARGO_PATH': 'cargo_path', 'EXAMPLE': 'other', 'PATH': 'common:first:second'}
    """
    keys = set(first.keys()).union(second.keys())
    merged = dict()
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
        erdpy deps install nodejs
        erdpy deps install wasm-opt

    Alternatively, pass the "--no-wasm-opt" argument in order to skip the optimization step.
        """)
