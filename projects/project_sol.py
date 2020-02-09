import subprocess

from erdpy import dependencies, errors, myprocess, utils
from erdpy.projects.project_base import Project


class ProjectSol(Project):
    def __init__(self, directory):
        super().__init__(directory)

    def perform_build(self):
        try:
            pass
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def get_dependencies(self):
        return ["soll", "llvm-for-soll"]
