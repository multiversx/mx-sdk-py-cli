import logging
from typing import List
from erdpy import dependencies, myprocess, utils
from erdpy.projects.interfaces import IProject

logger = logging.getLogger("wabt")


def generate_artifacts(project: IProject):
    wabt_module = dependencies.get_module_by_key("wabt")
    wabt_env = wabt_module.get_env()
    wasm_file = project.get_file_wasm()
    wat_file = wasm_file.with_suffix(".wat")
    imports_file = wasm_file.with_suffix(".imports.json")

    logger.info(f"Convert WASM to WAT: {wasm_file}")
    myprocess.run_process(
        ["wasm2wat", str(wasm_file), "-o", str(wat_file)],
        env=wabt_env
    )

    logger.info(f"Extract imports: {wasm_file}")
    imports_text = myprocess.run_process(
        ["wasm-objdump", str(wasm_file), "--details", "--section", "Import"],
        env=wabt_env,
        dump_to_stdout=False
    )
    imports = _parse_imports_text(imports_text)
    utils.write_json_file(str(imports_file), imports)


def _parse_imports_text(text: str) -> List[str]:
    lines = [line for line in text.splitlines() if "func" in line and "env" in line]
    imports = [line.split(".")[-1] for line in lines]
    return imports
