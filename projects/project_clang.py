import binascii
import logging
import subprocess
from os import path
from pathlib import Path

from erdpy import dependencies, errors, myprocess, utils
from erdpy.projects import Project

logger = logging.getLogger("ProjectClang")


class ProjectClang(Project):
    def perform_build(self):
        self.file_ll = self.unit.with_suffix(".ll")
        self.file_o = self.unit.with_suffix(".o")
        self.file_export = self.unit.with_suffix(".export")

        try:
            self._do_clang()
            self._do_llc()
            self._do_wasm()
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def get_main_unit(self):
        return self._get_single_unit(".c")

    def _do_clang(self):
        logger.info("_do_clang")
        tool = path.join(self._get_llvm_path(), "clang-9")
        args = [tool, "-cc1", "-Ofast", "-emit-llvm",
                "-triple=wasm32-unknown-unknown-wasm", str(self.unit)]
        myprocess.run_process(args)

    def _do_llc(self):
        logger.info("_do_llc")
        tool = path.join(self._get_llvm_path(), "llc")
        args = [tool, "-O3", "-filetype=obj", self.file_ll, "-o", self.file_o]
        myprocess.run_process(args)

    def _do_wasm(self):
        logger.info("_do_wasm")
        tool = path.join(self._get_llvm_path(), "wasm-ld")
        undefined_file = self._get_undefined_file()
        args = [tool, "--verbose", "--no-entry", str(self.file_o), "-o", str(self.file_wasm),
                "--strip-all", f"-allow-undefined-file={str(undefined_file)}"]
        exports = self._get_exports()

        for export in exports:
            args.append(f"-export={export}")

        myprocess.run_process(args)

    def _get_llvm_path(self):
        return dependencies.get_install_directory("llvm-for-c")

    def _get_undefined_file(self):
        building_path = Path(__file__).parent.parent.joinpath("building")

        if self.debug:
            return building_path.joinpath("api_debug.txt")
        else:
            return building_path.joinpath("api.txt")

    def _get_exports(self):
        file_export = self._get_single_unit(".export")
        lines = utils.read_lines(file_export)
        return lines

    def get_dependencies(self):
        return ["llvm-for-c"]
