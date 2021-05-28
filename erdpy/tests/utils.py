import base64
import unittest
from pathlib import Path

from erdpy import projects, utils
from erdpy.accounts import Account
from erdpy.contracts import SmartContract


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.testdata = Path(__file__).parent.joinpath("testdata")
        self.testdata_out = Path(__file__).parent.joinpath("testdata-out")
        self.devnet_wallets = Path(__file__).parent.parent.joinpath("testnet", "wallets")

        utils.ensure_folder(self.testdata_out)


class ProjectTestCase(MyTestCase):
    def setUp(self):
        super().setUp()
        self.testdata = Path(__file__).parent.joinpath("testdata")
        self.environment = None
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

    def deploy(self, contract, owner=None):
        owner = owner or self.alice
        tx, address = self.environment.deploy_contract(contract, owner=owner)
        return tx, address

    def execute(self, contract, caller, function, arguments=None):
        self.environment.execute_contract(contract, caller, function, arguments)

    def query_number(self, contract, function, arguments=None):
        result = self.query_first(contract, function, arguments)
        result = base64_to_int(result)
        return result

    def query_first(self, contract, function, arguments=None):
        results = self.environment.query_contract(contract, function, arguments)
        result = results[0]
        return result


def base64_to_int(data):
    output = base64.b64decode(data)
    output = output.hex()
    output = int(output, 16)
    return output
