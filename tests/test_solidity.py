import unittest
import logging
from pathlib import Path

from erdpy import projects

logging.basicConfig(level=logging.DEBUG)

class ProjectSolidityTestCase(unittest.TestCase):
    def setUp(self):
        self.testdata = Path(__file__).parent.joinpath("testdata")

    def test_build(self):
        project = projects.load_project(self.testdata.joinpath("solidity_hello"))
        project.build(debug=False)

    def test_deploy_interact(self):
        pass