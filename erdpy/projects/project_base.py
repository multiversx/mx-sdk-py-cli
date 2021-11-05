import glob
import logging
import shutil
from os import path
from pathlib import Path
from typing import Any, Dict, List, Union, cast

from erdpy import dependencies, errors, myprocess, utils
from erdpy.dependencies.modules import StandaloneModule

logger = logging.getLogger("Project")


class Project:

    def __init__(self, directory: Path):
        self.path = directory.expanduser().resolve()
        self.directory = str(self.path)

    def build(self, options: Union[Dict[str, Any], None] = None) -> Path:
        self.options = options or dict()
        self.debug = self.options.get("debug", False)
        self._ensure_dependencies_installed()
        self.perform_build()
        return self._do_after_build()

    def clean(self):
        utils.remove_folder(self.get_output_folder())

    def _ensure_dependencies_installed(self):
        module_keys = self.get_dependencies()
        for module_key in module_keys:
            dependencies.install_module(module_key)

    def get_dependencies(self) -> List[str]:
        raise NotImplementedError()

    def perform_build(self) -> None:
        raise NotImplementedError()

    def get_file_wasm(self):
        return self.find_file_in_output("*.wasm")

    def find_file_globally(self, pattern: str) -> Path:
        return self.find_file_in_folder(self.path, pattern)

    def find_file_in_output(self, pattern: str) -> Path:
        folder = self.path / 'output'
        return self.find_file_in_folder(folder, pattern)

    def find_file_in_folder(self, folder: Path, pattern: str) -> Path:
        files = list(folder.rglob(pattern))

        if len(files) == 0:
            raise errors.KnownError(f"No file matches pattern [{pattern}].")
        if len(files) > 1:
            logger.warning(f"More files match pattern [{pattern}]. Will pick first:\n{files}")

        file = folder / files[0]
        return Path(file).resolve()

    def _do_after_build(self) -> Path:
        raise NotImplementedError()

    def _copy_to_output(self, source: Path, destination: str = None) -> Path:
        output_folder = self.get_output_folder()
        utils.ensure_folder(output_folder)
        destination = path.join(output_folder, destination) if destination else output_folder
        output_wasm_file = shutil.copy(str(source), destination)
        return Path(output_wasm_file)

    def get_output_folder(self):
        return path.join(self.directory, "output")

    def get_bytecode(self):
        bytecode = utils.read_file(self.get_file_wasm(), binary=True)
        bytecode_hex = bytecode.hex()
        return bytecode_hex

    def load_config(self):
        config_file = self.get_config_file()
        config = utils.read_json_file(str(config_file))
        return config

    def get_config_file(self):
        return self.path / 'elrond.json'

    def ensure_config_file(self):
        config_file = self.get_config_file()
        if not config_file.exists():
            utils.write_json_file(str(config_file), self.default_config())
            logger.info("created default configuration in elrond.json")

    def default_config(self):
        return dict()

    def run_tests(self, tests_directory: Path, wildcard: str = ""):
        vmtools = cast(StandaloneModule, dependencies.get_module_by_key("vmtools"))
        tool_env = vmtools.get_env()
        tool = path.join(vmtools.get_parent_directory(), "mandos-test")
        test_folder = self.directory / tests_directory

        if not wildcard:
            args = [tool, str(test_folder)]
            myprocess.run_process(args, env=tool_env)
        else:
            pattern = test_folder / wildcard
            test_files = glob.glob(str(pattern))

            for test_file in test_files:
                print("Run test for:", test_file)
                args = [tool, test_file]
                myprocess.run_process(args, env=tool_env)
