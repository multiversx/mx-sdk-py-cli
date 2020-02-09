import subprocess

from erdpy import dependencies, errors, myprocess, utils
from erdpy.projects import Project


class ProjectSol(Project):
    def perform_build(self):
        try:
            pass
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def get_dependencies(self):
        return ["soll", "llvm-for-soll"]
