import unittest
from pathlib import Path

from multiversx_sdk_cli import projects, utils
from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.contracts import SmartContract
from multiversx_sdk_cli.workstation import get_tools_folder


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.testdata = Path(__file__).parent.joinpath("testdata")
        self.testdata_out = Path(__file__).parent.joinpath("testdata-out")
        self.devnet_wallets = get_tools_folder() / "testwallets" /"latest"

        utils.ensure_folder(self.testdata_out)


class ProjectTestCase(MyTestCase):
    def setUp(self):
        super().setUp()
        self.testdata = Path(__file__).parent.joinpath("testdata")
        self.alice = Account(
            "aaaaaaaa112233441122334411223344112233441122334411223344aaaaaaaa")
        self.bob = Account(
            "bbbbbbbb112233441122334411223344112233441122334411223344bbbbbbbb")
        self.carol = Account(
            "cccccccc112233441122334411223344112233441122334411223344cccccccc")
        self.david = Account(
            "dddddddd112233441122334411223344112233441122334411223344dddddddd")

    def build(self, name):
        project = self.load_project(name)
        project.build()
        bytecode = project.get_bytecode()
        contract = SmartContract(bytecode=bytecode)
        return project, contract

    def load_project(self, name):
        return projects.load_project(self.testdata.joinpath(name))
