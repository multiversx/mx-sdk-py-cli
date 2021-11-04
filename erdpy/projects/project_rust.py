import logging
import shutil
import subprocess
from os import path
from pathlib import Path
from typing import Any, Dict, cast

from erdpy import dependencies, errors, myprocess, utils
from erdpy.projects.project_base import Project

logger = logging.getLogger("ProjectRust")


class ProjectRust(Project):
    def __init__(self, directory):
        super().__init__(directory)
        self.cargo_file = self.get_cargo_file()

    def clean(self):
        super().clean()
        utils.remove_folder(path.join(self.directory, "wasm", "target"))

    def get_cargo_file(self):
        cargo_path = self.path / 'Cargo.toml'
        return CargoFile(cargo_path)

    def get_meta_folder(self):
        return self.path / 'meta'

    def perform_build(self):
        meta = self.has_meta()
        try:
            if meta:
                # The meta crate allows contract developers to add extra
                # preparation steps before building.
                self.run_meta()
            self.run_cargo()

            # ABI generated separately for backwards compatibility
            if not meta:
                self.generate_abi()
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def run_cargo(self):
        env = self.get_env()

        args = [
            "cargo",
            "build",
            "--target=wasm32-unknown-unknown",
            "--release",
            "--out-dir",
            self.get_output_folder(),
            "-Z"
            "unstable-options"
        ]
        self.decorate_cargo_args(args)

        if not self.options.get("wasm_symbols"):
            env["RUSTFLAGS"] = "-C link-arg=-s"

        cwd = self.path / 'wasm'
        return_code = myprocess.run_process_async(args, env=env, cwd=str(cwd))
        if return_code != 0:
            raise errors.BuildError(f"error code = {return_code}, see output")

    def run_meta(self):
        cwd = self.get_meta_folder()
        env = self.get_env()

        args = [
            "cargo",
            "run",
        ]

        return_code = myprocess.run_process_async(args, env=env, cwd=str(cwd))
        if return_code != 0:
            raise errors.BuildError(f"error code = {return_code}, see output")

    def decorate_cargo_args(self, args):
        target_dir = self.options.get("cargo_target_dir")
        if target_dir:
            args.extend(["--target-dir", target_dir])

    def generate_abi(self):
        if not self.has_abi():
            return

        args = [
            "cargo",
            "run"
        ]
        self.decorate_cargo_args(args)

        env = self.get_env()
        cwd = path.join(self.directory, "abi")
        sink = myprocess.FileOutputSink(self.get_abi_filepath())
        return_code = myprocess.run_process_async(args, env=env, cwd=cwd, stdout_sink=sink)
        if return_code != 0:
            raise errors.BuildError(f"error code = {return_code}, see output")

        utils.prettify_json_file(self.get_abi_filepath())

    def has_meta(self):
        return (self.get_meta_folder() / "Cargo.toml").exists()

    def has_abi(self):
        return (self.get_abi_folder() / "Cargo.toml").exists()

    def get_abi_filepath(self):
        return self.get_abi_folder() / "abi.json"

    def get_abi_folder(self):
        return Path(self.directory, "abi")

    def _do_after_build(self) -> Path:
        original_name = self.cargo_file.package_name
        wasm_base_name = self.cargo_file.package_name.replace("-", "_")
        wasm_file = Path(self.get_output_folder(), f"{wasm_base_name}_wasm.wasm").resolve()
        wasm_file_renamed = self.options.get("wasm_name")
        if not wasm_file_renamed:
            wasm_file_renamed = f"{original_name}.wasm"
        wasm_file_renamed_path = Path(self.get_output_folder(), wasm_file_renamed)
        shutil.move(str(wasm_file), wasm_file_renamed_path)

        if self.has_abi():
            abi_file = self.get_abi_filepath()
            abi_file_renamed = Path(self.get_output_folder(), f"{original_name}.abi.json")
            shutil.move(abi_file, abi_file_renamed)

        return wasm_file_renamed_path

    def get_dependencies(self):
        return ["rust"]

    def get_env(self):
        return dependencies.get_module_by_key("rust").get_env()


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

    def get_dependency(self, name) -> Dict[str, Any]:
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
