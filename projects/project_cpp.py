import logging
import subprocess
from os import path

from erdpy import dependencies, errors, myprocess, utils
from erdpy.projects.project_base import Project

logger = logging.getLogger("ProjectCpp")


class ProjectCpp(Project):
    def __init__(self, directory):
        super().__init__(directory)

    def perform_build(self):
        self.build_configuration = CppBuildConfiguration(self, self.debug)
        self.unit = self.find_file("*.cpp")
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
            "-ObjC++",
            "-std=c++17",
            "-nostdinc++",
            "-nobuiltininc",
            "-fno-builtin",
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
            "-o", self.get_file_wasm(),
            "--strip-all",
            f"--allow-undefined",
            "--demangle"
        ]

        if self.options.get("verbose", False):
            args.append("--verbose")

        for export in self.build_configuration.exports:
            args.append(f"-export={export}")

        myprocess.run_process(args)

    def get_file_wasm(self):
        return self.find_file("*.cpp").with_suffix(".wasm")

    def _get_llvm_path(self):
        return dependencies.get_install_directory("llvm")

    def get_dependencies(self):
        return ["llvm"]


class CppBuildConfiguration:
    def __init__(self, project, debug):
        self.project = project
        self.debug = debug
        self.exports = self._get_exports()

    def _get_exports(self):
        file_export = self.project.find_file("*.export")
        lines = utils.read_lines(file_export)
        return lines
