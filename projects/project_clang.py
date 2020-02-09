import binascii
import logging
import subprocess
from os import path
from pathlib import Path

from erdpy import dependencies, errors, myprocess, utils
from erdpy.projects.project_base import Project

logger = logging.getLogger("ProjectClang")


class ProjectClang(Project):
    def __init__(self, directory):
        super().__init__(directory)

    def perform_build(self):
        self.build_configuration = BuildConfiguration(self, self.debug)
        self.unit = self.find_file(".c")
        self.file_ll = self.unit.with_suffix(".ll")
        self.file_o = self.unit.with_suffix(".o")
        self.file_export = self.unit.with_suffix(".export")

        try:
            self._do_clang()
            self._do_llc()
            self._do_wasm()
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def _do_clang(self):
        logger.info("_do_clang")
        tool = path.join(self._get_llvm_path(), "clang-9")
        args = [
            tool,
            "-cc1", "-Ofast", "-emit-llvm",
            "-triple=wasm32-unknown-unknown-wasm",
            str(self.unit)
        ]
        myprocess.run_process(args)

    def _do_llc(self):
        logger.info("_do_llc")
        tool = path.join(self._get_llvm_path(), "llc")
        args = [tool, "-O3", "-filetype=obj", self.file_ll, "-o", self.file_o]
        myprocess.run_process(args)

    def _do_wasm(self):
        logger.info("_do_wasm")
        tool = path.join(self._get_llvm_path(), "wasm-ld")
        args = [
            tool,
            "--verbose",
            "--no-entry",
            str(self.file_o),
            "-o", self.get_file_wasm(),
            "--strip-all",
            f"-allow-undefined-file={str(self.build_configuration.undefined_file)}"
        ]

        for export in self.build_configuration.exports:
            args.append(f"-export={export}")

        myprocess.run_process(args)

    def get_file_wasm(self):
        return self.unit.with_suffix(".wasm")

    def _get_llvm_path(self):
        return dependencies.get_install_directory("llvm-for-c")

    def get_dependencies(self):
        return ["llvm-for-c"]


class BuildConfiguration:
    def __init__(self, project, debug):
        self.project = project
        self.debug = debug
        self.exports = self._get_exports()
        self.undefined_file = self._get_undefined_file()

    def _get_exports(self):
        file_export = self.project.find_file(".export")
        lines = utils.read_lines(file_export)
        return lines

    def _get_undefined_file(self):
        package_path = Path(__file__).parent

        if self.debug:
            return package_path.joinpath("list_api_debug.txt")
        else:
            return package_path.joinpath("list_api.txt")
