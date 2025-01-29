import logging
import subprocess
from pathlib import Path
from typing import Any, List, Optional, Union

from multiversx_sdk_cli import errors

logger = logging.getLogger("myprocess")


def run_process(
    args: List[str],
    env: Any = None,
    dump_to_stdout: bool = True,
    cwd: Optional[Union[str, Path]] = None,
) -> str:
    logger.info(f"run_process: {args}, in folder: {cwd}")

    try:
        output = subprocess.check_output(
            args,
            shell=False,
            universal_newlines=True,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=cwd,
        )
        logger.info("Successful run. Output:")
        if dump_to_stdout:
            print(output or "[No output]")
        return output
    except subprocess.CalledProcessError as error:
        raise errors.ExternalProcessError(error.cmd, error.output)
