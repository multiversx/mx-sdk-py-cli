import logging
from pathlib import Path

from multiversx_sdk_cli import utils

logging.basicConfig(level=logging.INFO)


class TestProjectRust:
    def test_set_up(self):
        self.testdata = Path(__file__).parent.joinpath("testdata")
        self.testdata_out = Path(__file__).parent.joinpath("testdata-out")
        utils.ensure_folder(self.testdata_out)
