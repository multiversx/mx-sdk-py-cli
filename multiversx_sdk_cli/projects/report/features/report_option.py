from abc import abstractmethod
from pathlib import Path
from typing import Any, Optional


class ReportFeature:
    """
    Base class for any feature in a report.

    A feature represents a column in a report.
    The name argument will appear as the column header in a report.
    The implementation of the extract method will determine the contents of each cell in said column.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def extract(self, wasm_path: Path) -> str:
        pass

    def requires_twiggy_paths(self) -> bool:
        return False


def str_or_default(field: Optional[Any], default: str = '-') -> str:
    if field is None:
        return default
    return str(field)
