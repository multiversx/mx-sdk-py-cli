import logging
import os
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
        self.build_configuration = ClangBuildConfiguration(self, self.debug)
        self.unit = self.find_file_globally("*.c")
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
            "-cc1", "-emit-llvm",
            "-triple=wasm32-unknown-unknown-wasm",
        ]
        if self.options.get("optimized", False):
            args.append("-Ofast")
        else:
            args.append("-O0")
        args.append(str(self.unit))
        myprocess.run_process(args)

    def _do_llc(self):
        logger.info("_do_llc")
        tool = path.join(self._get_llvm_path(), "llc")
        args = [tool]
        if self.options.get("optimized", False):
            args.append("-O3")
        else:
            args.append("-O0")
        args.extend(["-filetype=obj", self.file_ll, "-o", self.file_o])
        myprocess.run_process(args)

    def _do_wasm(self):
        logger.info("_do_wasm")
        tool = path.join(self._get_llvm_path(), "wasm-ld")
        args = [
            tool,
            "--no-entry",
            str(self.file_o),
            "-o", self.find_file_globally("*.c").with_suffix(".wasm"),
            "--strip-all",
            "-allow-undefined"
        ]

        if self.options.get("verbose", False):
            args.append("--verbose")

        for export in self.build_configuration.exports:
            args.append(f"-export={export}")

        myprocess.run_process(args)

    def _copy_build_artifacts_to_output(self):
        source_file = self.find_file_globally("*.c")
        self._copy_to_output(source_file.with_suffix(".wasm"))
        os.remove(source_file.with_suffix(".wasm"))
        os.remove(source_file.with_suffix(".ll"))
        os.remove(source_file.with_suffix(".o"))

    def _get_llvm_path(self):
        return dependencies.get_module_directory("llvm")

    def get_dependencies(self):
        return ["llvm"]


class ClangBuildConfiguration:
    def __init__(self, project, debug):
        self.project = project
        self.debug = debug
        self.exports = self._get_exports()

    def _get_exports(self):
        file_export = self.project.find_file_globally("*.export")
        lines = utils.read_lines(file_export)
        return lines

