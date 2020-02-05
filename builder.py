
import logging
import os
import subprocess
from os import path
from pathlib import Path

from erdpy import config, dependencies, environment, errors, utils

logger = logging.getLogger("builder")


def build_project(directory, debug=False):
    logger.info("build_project.directory: %s", directory)
    logger.info("build_project.debug: %s", debug)

    _guard_is_directory(directory)
    codebase = _create_codebase(directory)
    codebase.build(debug)


def _guard_is_directory(directory):
    ok = path.isdir(directory)
    if not ok:
        raise errors.BadDirectory(directory)


def _create_codebase(directory):
    if _is_source_C(directory):
        return CCodebase(directory)
    if _is_source_sol(directory):
        return SolCodebase(directory)
    if _is_source_rust(directory):
        return RustCodebase(directory)


def _is_source_C(directory):
    return _directory_contains_file(directory, ".c")


def _is_source_sol(directory):
    return _directory_contains_file(directory, ".sol")


def _is_source_rust(directory):
    return _directory_contains_file(directory, "Cargo.toml")


def _directory_contains_file(directory, name_suffix):
    for file in os.listdir(directory):
        if file.lower().endswith(name_suffix.lower()):
            return True


class Codebase:
    def __init__(self, directory):
        self.directory = directory

    def build(self, debug):
        self.debug = debug
        self._ensure_dependencies_installed()

    def _ensure_dependencies_installed(self):
        module_keys = self.get_dependencies()
        for module_key in module_keys:
            dependencies.install_module(module_key)

    def get_dependencies(self):
        return []

    def _get_single_unit(self, suffix):
        all_files = os.listdir(self.directory)
        files = [file for file in all_files if file.endswith(suffix)]

        if len(files) == 0:
            raise errors.KnownError(f"No unit: [{suffix}].")
        if len(files) > 1:
            raise errors.KnownError(
                f"More [{suffix}] units aren't supported yet.")

        file = path.join(self.directory, files[0])
        return Path(file).resolve()


class CCodebase(Codebase):
    def build(self, debug):
        super().build(debug)

        self.unit = self._get_main_unit()
        self.file_ll = self.unit.with_suffix(".ll")
        self.file_o = self.unit.with_suffix(".o")
        self.file_wasm = self.unit.with_suffix(".wasm")
        self.file_export = self.unit.with_suffix(".export")

        try:
            self._do_clang()
            self._do_llc()
            self._do_wasm()
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def _get_main_unit(self):
        return self._get_single_unit(".c")

    def _do_clang(self):
        logger.info("CCodebase._do_clang")
        tool = path.join(self._get_llvm_path(), "clang-9")
        args = [tool, "-cc1", "-Ofast", "-emit-llvm",
                "-triple=wasm32-unknown-unknown-wasm", str(self.unit)]
        utils.run_process(args)

    def _do_llc(self):
        logger.info("CCodebase._do_llc")
        tool = path.join(self._get_llvm_path(), "llc")
        args = [tool, "-O3", "-filetype=obj", self.file_ll, "-o", self.file_o]
        utils.run_process(args)

    def _do_wasm(self):
        logger.info("CCodebase._do_wasm")
        tool = path.join(self._get_llvm_path(), "wasm-ld")
        undefined_file = self._get_undefined_file()
        args = [tool, "--verbose", "--no-entry", str(self.file_o), "-o", str(self.file_wasm),
                "--strip-all", f"-allow-undefined-file={str(undefined_file)}"]
        exports = self._get_exports()

        for export in exports:
            args.append(f"-export={export}")

        utils.run_process(args)

    def _get_llvm_path(self):
        return dependencies.get_install_directory("llvm-for-c")

    def _get_undefined_file(self):
        file_parent = Path(__file__).parent
        print(Path(__file__).parent.joinpath("builder_api_debug.txt"))

        if self.debug:
            return file_parent.joinpath("builder_api_debug.txt")
        else:
            return file_parent.joinpath("builder_api.txt")

    def _get_exports(self):
        file_export = self._get_single_unit(".export")
        lines = utils.read_lines(file_export)
        return lines

    def get_dependencies(self):
        return ["llvm-for-c"]


class SolCodebase(Codebase):
    pass


class RustCodebase(Codebase):
    pass
