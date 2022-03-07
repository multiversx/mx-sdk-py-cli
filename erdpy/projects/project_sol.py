import logging
from pathlib import Path
from typing import List

from erdpy.projects.project_base import Project

logger = logging.getLogger("ProjectSol")


class ProjectSol(Project):
    def __init__(self, directory: Path):
        super().__init__(directory)

    def perform_build(self):
        pass

    def get_dependencies(self) -> List[str]:
        return []

    def _do_after_build_custom(self) -> List[Path]:
        raise NotImplementedError()
