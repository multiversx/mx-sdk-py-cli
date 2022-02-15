from pathlib import Path
from typing import Optional

from .report_option import ReportOption, str_or_default


class Size(ReportOption):
    def apply(self, wasm_path: Path):
        size = get_file_size(wasm_path)
        return str_or_default(size)


def get_file_size(file_path: Path) -> Optional[int]:
    try:
        return int(file_path.stat().st_size)
    except FileNotFoundError:
        return None
