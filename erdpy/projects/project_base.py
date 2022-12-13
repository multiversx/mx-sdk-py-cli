from abc import abstractmethod
import glob
import logging
import shutil
from os import path
from pathlib import Path
from typing import Any, Dict, List, Union, cast, final

from erdpy import dependencies, errors, myprocess, utils
from erdpy.dependencies.modules import StandaloneModule
from erdpy.projects import eei_checks
from erdpy.projects.interfaces import IProject

logger = logging.getLogger("Project")


class Project(IProject):

    def __init__(self, directory: Path):
        self.path = directory.expanduser().resolve()
        self.directory = str(self.path)

    def build(self, options: Union[Dict[str, Any], None] = None) -> List[Path]:
        self.options = options or dict()
        self.debug = self.options.get("debug", False)
        self._ensure_dependencies_installed()
        self.perform_build()
        contract_paths = self._do_after_build_custom()
        self._do_after_build_core()
        return contract_paths

    def get_option(self, option_name: str) -> Any:
        return self.options.get(option_name, None)

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

    def get_file_wasm(self) -> Path:
        return self.find_file_in_output("*.wasm")

    def find_file_globally(self, pattern: str) -> Path:
        return self.find_file_in_folder(self.path, pattern)

    def find_file_in_output(self, pattern: str) -> Path:
        folder = self.get_output_folder()
        return self.find_file_in_folder(Path(folder), pattern)

    def find_file_in_folder(self, folder: Path, pattern: str) -> Path:
        files = list(folder.rglob(pattern))

        if len(files) == 0:
            raise errors.KnownError(f"No file matches pattern [{pattern}].")
        if len(files) > 1:
            logger.warning(f"More files match pattern [{pattern}]. Will pick first:\n{files}")

        file = folder / files[0]
        return Path(file).resolve()
    
    def find_wasm_files(self):
        output_folder = Path(self.get_output_folder())
        wasm_files = output_folder.rglob("*.wasm")
        main_wasm_files = list(filter(lambda wasm_path: not wasm_path.name.endswith("-dbg.wasm"), wasm_files))
        return main_wasm_files

    @abstractmethod
    def _do_after_build_custom(self) -> List[Path]:
        raise NotImplementedError()

    @final
    def _do_after_build_core(self):
        # TODO: Remove this, in the future
        eei_checks.check_compatibility(self)

    def _copy_to_output(self, source: Path, destination: Union[str, None] = None) -> Path:
        output_folder = self.get_output_folder()
        utils.ensure_folder(output_folder)
        destination = path.join(output_folder, destination) if destination else output_folder
        output_wasm_file = shutil.copy(str(source), destination)
        return Path(output_wasm_file)

    def get_output_folder(self):
        return path.join(self.directory, "output")
    
    def get_wasm_default_name(self, suffix: str = "") -> str:
        return f"{self.path.name}{suffix}.wasm"
    
    def get_wasm_path(self, wasm_name: str) -> Path:
        return Path(self.get_output_folder(), wasm_name).resolve()

    def get_wasm_default_path(self) -> Path:
        return self.get_wasm_path(self.get_wasm_default_name())

    def get_wasm_view_default_path(self) -> Path:
        return self.get_wasm_path(self.get_wasm_default_name("-view"))

    def get_bytecode(self):
        bytecode: bytes = cast(bytes, utils.read_file(self.get_file_wasm(), binary=True))
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

    def default_config(self) -> Dict[str, Any]:
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

def glob_files(folder: Path, pattern: str) -> List[Path]:
    files = folder.rglob(pattern)
    return [Path(folder / file).resolve() for file in files]

def exclude_files(files: List[Path], to_exclude: List[Path]) -> List[Path]:
    return list(set(files).difference(to_exclude))

def rename_wasm_files(paths: List[Path], name: Union[str, None]) -> List[Path]:
    if name is None:
        return paths
    new_paths = [adjust_wasm_filename(path, name) for path in paths]
    for old_path, new_path in zip(paths, new_paths):
        old_path.rename(new_path)
    return new_paths

def get_contract_suffix(name: str) -> str:
    for suffix in ["-view.wasm", ".wasm"]:
        if name.endswith(suffix):
            return suffix
    return ""

def remove_suffix(name: str, suffix: str) -> str:
    if not name.endswith(suffix) or len(suffix) == 0:
        return name
    return name[:-len(suffix)]

def adjust_wasm_filename(path: Path, name_hint: str) -> Path:
    """
    Adjusts the wasm's filename by using a name hint

    >>> adjust_wasm_filename(Path("test/my-contract.wasm"), "hello.wasm")
    PosixPath('test/hello.wasm')
    >>> adjust_wasm_filename(Path("test/my-contract-view.wasm"), "hello.wasm")
    PosixPath('test/hello-view.wasm')
    >>> adjust_wasm_filename(Path("test/my-contract-view.wasm"), "hello")
    PosixPath('test/hello-view.wasm')
    >>> adjust_wasm_filename(Path("test/my-contract.wasm"), "world-view.wasm")
    PosixPath('test/world-view.wasm')
    >>> adjust_wasm_filename(Path("test/my-contract-view.wasm"), "world-view.wasm")
    PosixPath('test/world-view-view.wasm')
    """
    new_name = remove_suffix(name_hint, ".wasm") + get_contract_suffix(path.name)
    return path.with_name(new_name)
