import logging
from pathlib import Path

from multiversx_sdk_cli import dependencies, myprocess, utils
from multiversx_sdk_cli.errors import BadFile
from multiversx_sdk_cli.projects.report.features.report_option import ReportFeature

logger = logging.getLogger("projects.report.options.twiggy_paths_check")


class TwiggyPathsCheck(ReportFeature):
    def __init__(self, name: str, pattern: str) -> None:
        super().__init__(name)

        self.pattern = pattern

    def extract(self, wasm_path: Path) -> str:
        twiggy_paths_path = _get_twiggy_paths_path(wasm_path)
        try:
            text = utils.read_text_file(twiggy_paths_path)
            return str(self.pattern in text)
        except BadFile:
            return 'N/A'

    def requires_twiggy_paths(self):
        return True


def run_twiggy_paths(wasm_path: Path) -> Path:
    rust = dependencies.get_module_by_key("rust")
    debug_wasm_path = _get_debug_wasm_path(wasm_path)
    twiggy_paths_args = ["twiggy", "paths", str(debug_wasm_path)]
    output = myprocess.run_process(twiggy_paths_args, env=rust.get_env(), cwd=debug_wasm_path.parent, dump_to_stdout=False)
    output_path = _get_twiggy_paths_path(wasm_path)
    utils.write_file(output_path, output)
    logger.info(f"Twiggy paths output path: {output_path}")
    return output_path


def _replace_file_suffix(file_path: Path, suffix: str) -> Path:
    new_name = file_path.stem + suffix
    return file_path.with_name(new_name)


def _add_file_prefix(file_path: Path, prefix: str) -> Path:
    new_name = prefix + file_path.name
    return file_path.with_name(new_name)


def _get_debug_wasm_path(wasm_path: Path) -> Path:
    """
>>> _get_debug_wasm_path(Path('test/contract.wasm'))
PosixPath('test/contract-dbg.wasm')
    """
    return _replace_file_suffix(wasm_path, '-dbg.wasm')


def _get_twiggy_paths_path(wasm_path: Path) -> Path:
    """
>>> _get_twiggy_paths_path(Path('test/contract.wasm'))
PosixPath('test/twiggy-paths-contract-dbg.txt')
    """
    txt_file_path = _replace_file_suffix(wasm_path, '-dbg.txt')
    return _add_file_prefix(txt_file_path, 'twiggy-paths-')
