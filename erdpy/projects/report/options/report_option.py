from abc import abstractmethod
from pathlib import Path
from typing import Any, Optional


class ReportOption:
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def apply(self, wasm_path: Path) -> str:
        pass

    def requires_twiggy_paths(self) -> bool:
        return False


def str_or_default(field: Optional[Any], default: str = '-') -> str:
    if field is None:
        return default
    return str(field)
