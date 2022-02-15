from typing import List
from .report_option import ReportOption
from .size import Size
from .twiggy_paths_check import TwiggyPathsCheck

def get_default_report_options() -> List[ReportOption]:
    return [
        Size("size"),
        TwiggyPathsCheck("has-allocator", pattern="wee_alloc::"),
        TwiggyPathsCheck("has-format", pattern="core::fmt"),
    ]
