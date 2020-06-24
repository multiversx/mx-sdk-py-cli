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
        undefined_file = str(self.build_configuration.undefined_file)
        args = [
            tool,
            "--no-entry",
            str(self.file_o),
            "-o", self.find_file_globally("*.c").with_suffix(".wasm"),
            "--strip-all",
            f"-allow-undefined-file={undefined_file}"
        ]

        if self.options.get("verbose", False):
            args.append("--verbose")

        for export in self.build_configuration.exports:
            args.append(f"-export={export}")

        myprocess.run_process(args)

    def _copy_build_artifacts_to_output(self):
        wasm_file = self.find_file_globally("*.c").with_suffix(".wasm")
        self._copy_to_output(wasm_file)

    def _get_llvm_path(self):
        return dependencies.get_install_directory("llvm")

    def get_dependencies(self):
        return ["llvm"]


class ClangBuildConfiguration:
    def __init__(self, project, debug):
        self.project = project
        self.debug = debug
        self.exports = self._get_exports()
        self.undefined_file = self._get_undefined_file()

    def _get_exports(self):
        file_export = self.project.find_file_globally("*.export")
        lines = utils.read_lines(file_export)
        return lines

    def _get_undefined_file(self):
        package_path = Path(__file__).parent
        # TODO: remove this logic
        if self.debug:
            return package_path.joinpath("list_api_debug.txt")
        else:
            return package_path.joinpath("list_api.txt")
