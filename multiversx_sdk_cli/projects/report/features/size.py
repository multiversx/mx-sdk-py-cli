from pathlib import Path
from typing import Optional

from .report_option import ReportFeature, str_or_default


class Size(ReportFeature):
    def extract(self, wasm_path: Path):
        size = _get_file_size(wasm_path)
        return str_or_default(size)


def _get_file_size(file_path: Path) -> Optional[int]:
    try:
        return int(file_path.stat().st_size)
    except FileNotFoundError:
        return None
