import binascii
import glob
import logging
from os import path
from pathlib import Path

from erdpy import dependencies, errors, myprocess, utils

logger = logging.getLogger("Project")


class Project:
    def __init__(self, directory):
        self.directory = str(Path(directory).resolve())

    def build(self, options=None):
        self.options = options or dict()
        self.debug = self.options.get("debug", False)
        self._ensure_dependencies_installed()
        self.perform_build()
        self._create_deploy_files()

    def _ensure_dependencies_installed(self):
        module_keys = self.get_dependencies()
        for module_key in module_keys:
            dependencies.install_module(module_key)

    def get_dependencies(self):
        raise NotImplementedError()

    def perform_build(self):
        raise NotImplementedError()

    def get_file_wasm(self):
        raise NotImplementedError()

    def find_file(self, pattern):
        files = list(Path(self.directory).rglob(pattern))

        if len(files) == 0:
            raise errors.KnownError(f"No file matches pattern [{pattern}].")
        if len(files) > 1:
            logging.warning(f"More files match pattern [{pattern}]. Will pick first:\n{files}")

        file = path.join(self.directory, files[0])
        return Path(file).resolve()

    def _create_deploy_files(self):
        file_wasm = self.get_file_wasm()
        file_wasm_hex = file_wasm.with_suffix(".hex")

        with open(file_wasm, "rb") as file:
            bytecode_hex = binascii.hexlify(file.read())
        with open(file_wasm_hex, "wb+") as file:
            file.write(bytecode_hex)

    def get_bytecode(self):
        bytecode = utils.read_file(
            self.get_file_wasm().with_suffix(".hex"))
        return bytecode

    def run_tests(self, wildcard):
        testrunner_module = dependencies.get_module_by_key("testrunner")
        tool_directory = testrunner_module.get_directory()
        tool_env = testrunner_module.get_env()

        tool = path.join(tool_directory, "test")
        test_folder = path.join(self.directory, "test")
        pattern = path.join(test_folder, wildcard)
        test_files = glob.glob(pattern)

        for test_file in test_files:
            print("Run test for:", test_file)
            args = [tool, test_file]
            myprocess.run_process(args, env=tool_env)
