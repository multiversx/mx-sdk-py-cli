import logging
from pathlib import Path

from erdpy import dependencies, myprocess, utils
from erdpy.errors import BadFile
from erdpy.projects.report.options.report_option import ReportOption

logger = logging.getLogger("projects.report.options.twiggy_paths_check")


class TwiggyPathsCheck(ReportOption):
    def __init__(self, name: str, pattern: str) -> None:
        super().__init__(name)

        self.pattern = pattern


    def apply(self, wasm_path: Path) -> str:
        twiggy_paths_path = get_twiggy_paths_path(wasm_path)
        try:
            text = utils.read_text_file(twiggy_paths_path)
            return str(self.pattern in text)
        except BadFile:
            return 'N/A'
    
    def requires_twiggy_paths(self):
        return True


def replace_file_suffix(file_path: Path, suffix: str) -> Path:
    new_name = file_path.stem + suffix
    return file_path.with_name(new_name)


def get_debug_wasm_path(wasm_path: Path) -> Path:
    """
>>> get_debug_wasm_path(Path('test/contract.wasm'))
PosixPath('test/contract-dbg.wasm')
    """
    return replace_file_suffix(wasm_path, '-dbg.wasm')


def get_twiggy_paths_path(wasm_path: Path) -> Path:
    """
>>> replace_file_suffix(Path('test/contract.wasm'), '-paths.txt')
PosixPath('test/contract-paths.txt')
    """
    return replace_file_suffix(wasm_path, '-paths.txt')


def run_twiggy_paths(wasm_path: Path) -> Path:
    rust = dependencies.get_module_by_key("rust")
    debug_wasm_path = get_debug_wasm_path(wasm_path)
    twiggy_paths_args = ["twiggy", "paths", str(debug_wasm_path)]
    output = myprocess.run_process(twiggy_paths_args, env=rust.get_env(), cwd=debug_wasm_path.parent, dump_to_stdout=False)
    output_path = get_twiggy_paths_path(wasm_path)
    utils.write_file(output_path, output)
    logger.info(f"Twiggy paths output path: {output_path}")
    return output_path
