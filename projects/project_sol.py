import logging
import subprocess
from os import path
from pathlib import Path

from erdpy import dependencies, errors, myprocess, utils
from erdpy.projects.project_base import Project

logger = logging.getLogger("ProjectSol")


class ProjectSol(Project):
    def __init__(self, directory):
        super().__init__(directory)

    def perform_build(self):
        """
        See https://github.com/second-state/SOLL/blob/master/utils/ll2ewasm_sol
        """

        self.unit = self.find_file_globally("*.sol")
        self.unit_name = self.unit.stem
        self.file_ll = self.unit.with_suffix(".ll")
        self.file_functions = self.unit.with_suffix(".functions")
        self.file_main_ll = self.unit.with_suffix(".main.ll")
        self.file_bc = self.unit.with_suffix(".bc")
        self.file_o = self.unit.with_suffix(".o")

        try:
            self._create_main_ll()
            self._emit_LLVM()
            self._emit_funcions()
            self._do_llvm_link()
            self._do_llvm_opt()
            self._do_llc()
            self._do_wasm_ld()
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def _create_main_ll(self):
        logger.info("_create_main_ll")

        package_path = Path(__file__).parent
        template_path = package_path.joinpath("sol_main_ll.txt")
        template = utils.read_file(template_path)
        content = template.replace("{{NAME}}", self.unit_name)
        utils.write_file(self.file_main_ll, content)

    def _emit_LLVM(self):
        logger.info("_emit_LLVM")

        tool = self._get_soll_path()
        args = [tool, "-action", "EmitLLVM", str(self.unit)]
        output = myprocess.run_process(args)
        utils.write_file(self.file_ll, output)

    def _emit_funcions(self):
        logger.info("_emit_funcions")

        tool = self._get_soll_path()
        args = [tool, "-action", "EmitFuncSig", str(self.unit)]
        output = myprocess.run_process(args)
        utils.write_file(self.file_functions, output)

    def _do_llvm_link(self):
        logger.info("_do_llvm_link")

        tool = path.join(self._get_llvm_path(), "llvm-link")
        args = [tool, self.file_ll, self.file_main_ll, "-o", self.file_bc]
        myprocess.run_process(args)

    def _do_llvm_opt(self):
        logger.info("_do_llvm_opt")

        tool = path.join(self._get_llvm_path(), "opt")
        args = [tool, "-std-link-opts", "-Oz", "-polly", self.file_bc, "-o", self.file_bc]
        myprocess.run_process(args)

    def _do_llc(self):
        logger.info("_do_llc")

        tool = path.join(self._get_llvm_path(), "llc")
        args = [tool, "-O3", "-filetype=obj", self.file_bc, "-o", self.file_o]
        myprocess.run_process(args)

    def _do_wasm_ld(self):
        logger.info("_do_wasm_ld")

        tool = path.join(self._get_llvm_path(), "wasm-ld")
        args = [
            tool, 
            "--entry",
            "main",
            "--demangle",
            "--no-gc-sections",
            "--export-all",
            "--allow-undefined",
            "--verbose",
            self.file_o,
            "-o", self.get_file_wasm()
        ]
        myprocess.run_process(args)

    def _get_soll_path(self):
        directory = dependencies.get_module_directory("soll")
        return path.join(directory, "soll")

    def _get_llvm_path(self):
        return dependencies.get_module_directory("llvm")

    def get_dependencies(self):
        return ["soll", "llvm"]
