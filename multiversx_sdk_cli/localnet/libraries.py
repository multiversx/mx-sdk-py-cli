import logging
import os
import shutil
from pathlib import Path
from typing import List

from multiversx_sdk_cli.localnet.constants import FILE_MODE_EXECUTABLE

logger = logging.getLogger("localnet")


def copy_libraries(source: Path, destination: Path):
    libraries: List[Path] = list(source.glob("*.dylib")) + list(source.glob("*.so"))

    for library in libraries:
        logger.debug(f"Copying {library} to {destination}")
        shutil.copy(library, destination)
        os.chmod(destination / library.name, FILE_MODE_EXECUTABLE)
