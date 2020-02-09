import binascii
import logging
import subprocess
from os import path
from pathlib import Path

from erdpy import dependencies, errors, myprocess, utils
from erdpy.projects import Project

logger = logging.getLogger("ProjectRust")


class ProjectRust(Project):
    def perform_build(self):
        try:
            self.run_cargo()
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def run_cargo(self):
        if self.debug:
            args = ["cargo", "build"]
        else:
            args = ["cargo", "build", "--manifest-path", self.get_cargo_file(),
                    "--target=wasm32-unknown-unknown", "--release"]
        myprocess.run_process_async(args, env=self._get_env())

    def get_main_unit(self):
        name = self.get_package_name()
        return Path(self.directory, f"{name}.rust").resolve()

    def get_package_name(self):
        cargo = self.read_cargo()
        name = cargo["package"]["name"]
        return name

    def get_bin_name(self):
        cargo = self.read_cargo()
        name = cargo["bin"]["name"]
        return name

    def get_wasm_path(self):
        pass

    def read_cargo(self):
        return utils.read_toml_file(self.get_cargo_file())

    def get_cargo_file(self):
        return path.join(self.directory, "Cargo.toml")

    def get_dependencies(self):
        return ["rust"]

    def _get_env(self):
        return dependencies.get_module_by_key("rust").get_env()
