import base64
import logging
import unittest
from pathlib import Path

from erdpy import projects
from erdpy.accounts import Account
from erdpy.contracts import SmartContract
from erdpy.hosts import DebugHost
from erdpy.tests import utils

logging.basicConfig(level=logging.DEBUG)


class ProjectSolidityTestCase(utils.ProjectTestCase):
    def setUp(self):
        super().setUp()

    def test_solidity_hello(self):
        _, contract = self.build("solidity_hello")
        answer = None

        def myflow():
            nonlocal answer
            self.deploy(contract)
            answer = self.query_number(contract, "getValue()")

        self.host.run_flow(myflow)
        self.assertEqual(42, answer)

    def test_solidity_soll_001(self):
        _, contract = self.build("solidity_soll_001")
        answer = None

        def myflow():
            nonlocal answer
            self.deploy(contract)
            answer = self.query_number(
                contract, "add(uint256,uint256)", [30, 12])

        self.host.run_flow(myflow)
        self.assertEqual(42, answer)
