import logging
import subprocess
from os import path
from pathlib import Path
from typing import Any, MutableMapping

from erdpy import dependencies, errors, myprocess, utils
from erdpy.projects.project_base import Project

logger = logging.getLogger("ProjectRust")


class ProjectRust(Project):
    def __init__(self, directory):
        super().__init__(directory)
        self.cargo_file = self._get_cargo_file()

    def clean(self):
        super().clean()
        utils.remove_folder(path.join(self.directory, "wasm", "target"))

    def _get_cargo_file(self):
        cargo_path = path.join(self.directory, "Cargo.toml")
        return CargoFile(cargo_path)

    def perform_build(self):
        try:
            self.run_cargo()
            self._generate_abi()
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def run_cargo(self):
        env = self._get_env()

        if self.debug:
            args = ["cargo", "build"]
        else:
            args = [
                "cargo",
                "build",
                "--target=wasm32-unknown-unknown",
                "--release"
            ]

            env["RUSTFLAGS"] = "-C link-arg=-s"

        cwd = path.join(self.directory, "wasm")
        return_code = myprocess.run_process_async(args, env=env, cwd=cwd)
        if return_code != 0:
            raise errors.BuildError(f"error code = {return_code}, see output")

    def _generate_abi(self):
        if not self._has_abi():
            return

        env = self._get_env()
        cwd = path.join(self.directory, "abi")
        sink = myprocess.FileOutputSink(self._get_abi_filepath())
        return_code = myprocess.run_process_async(["cargo", "run"], env=env, cwd=cwd, stdout_sink=sink)
        if return_code != 0:
            raise errors.BuildError(f"error code = {return_code}, see output")

        utils.prettify_json_file(self._get_abi_filepath())

    def _has_abi(self):
        return Path(self._get_abi_folder(), "Cargo.toml").is_file()

    def _get_abi_filepath(self):
        return Path(self._get_abi_folder(), "abi.json")

    def _get_abi_folder(self):
        return Path(self.directory, "abi")

    def _copy_build_artifacts_to_output(self):
        name = self.cargo_file.package_name.replace("-", "_")
        wasm_file = Path(self.directory, "wasm", "target", "wasm32-unknown-unknown", "release", f"{name}_wasm.wasm").resolve()
        self._copy_to_output(wasm_file, f"{name}.wasm")

        if self._has_abi():
            self._copy_to_output(self._get_abi_filepath(), f"{name}.abi.json")

    def get_dependencies(self):
        return ["rust"]

    def _get_env(self):
        return dependencies.get_module_by_key("rust").get_env()


class CargoFile:
    def __init__(self, path):
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

    def save(self):
        utils.write_toml_file(self.path, self.data)

    def _get_package(self) -> MutableMapping[str, Any]:
        if "package" not in self.data:
            self.data["package"] = {}
        return self.data["package"]

    def get_dependencies(self) -> MutableMapping[str, Any]:
        if "dependencies" not in self.data:
            self.data["dependencies"] = {}
        return self.data["dependencies"]

    def get_dev_dependencies(self) -> MutableMapping[str, Any]:
        if "dev-dependencies" not in self.data:
            self.data["dev-dependencies"] = {}
        return self.data["dev-dependencies"]

    def get_dependency(self, name) -> MutableMapping[str, Any]:
        dependencies = self.get_dependencies()
        dependency = dependencies.get(name)
        if dependency is None:
            raise errors.BuildError(f"Can't get cargo dependency: {name}")
        return dependency

    def get_dev_dependency(self, name) -> MutableMapping[str, Any]:
        dependencies = self.get_dev_dependencies()
        dependency = dependencies.get(name)
        if dependency is None:
            raise errors.BuildError(f"Can't get cargo dev-dependency: {name}")
        return dependency
