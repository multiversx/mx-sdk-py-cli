from pathlib import Path
from typing import Any


class IProject():
    def get_option(self, option_name: str) -> Any:
        return None

    def get_file_wasm(self) -> Path:
        return Path("")
