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
        self._copy_build_artifacts_to_output()
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
        return self.find_file_in_output("*.wasm")

    def find_file_globally(self, pattern):
        folder = self.directory
        return self.find_file_in_folder(folder, pattern)

    def find_file_in_output(self, pattern):
        folder = path.join(self.directory, "output")
        return self.find_file_in_folder(folder, pattern)

    def find_file_in_folder(self, folder, pattern):
        files = list(Path(folder).rglob(pattern))

        if len(files) == 0:
            raise errors.KnownError(f"No file matches pattern [{pattern}].")
        if len(files) > 1:
            logging.warning(f"More files match pattern [{pattern}]. Will pick first:\n{files}")

        file = path.join(folder, files[0])
        return Path(file).resolve()

    def _copy_build_artifacts_to_output(self):
        raise NotImplementedError()

    def _copy_to_output(self, file):
        output_dir = path.join(self.directory, "output")
        utils.ensure_folder(output_dir)

    def _create_deploy_files(self):
        file_wasm = self.get_file_wasm()
        file_wasm_hex = file_wasm.with_suffix(".hex")

        with open(file_wasm, "rb") as file:
            bytecode_hex = binascii.hexlify(file.read())
        with open(file_wasm_hex, "wb+") as file:
            file.write(bytecode_hex)

    def get_bytecode(self):
        bytecode = utils.read_file(self.get_file_wasm().with_suffix(".hex"))
        return bytecode

    def run_tests(self, tests_directory, wildcard=None):
        testrunner_module = dependencies.get_module_by_key("arwentools")
        tool_directory = testrunner_module.get_directory()
        tool_env = testrunner_module.get_env()

        tool = path.join(tool_directory, "test")
        test_folder = path.join(self.directory, tests_directory)

        if not wildcard:
            args = [tool, test_folder]
            myprocess.run_process(args, env=tool_env)
        else:
            pattern = path.join(test_folder, wildcard)
            test_files = glob.glob(pattern)

            for test_file in test_files:
                print("Run test for:", test_file)
                args = [tool, test_file]
                myprocess.run_process(args, env=tool_env)
