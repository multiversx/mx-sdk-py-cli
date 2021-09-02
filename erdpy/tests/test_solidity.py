import base64
import logging
import unittest
from pathlib import Path

from erdpy.tests import utils

logging.basicConfig(level=logging.ERROR)


class ProjectSolidityTestCase(utils.ProjectTestCase):
    def setUp(self):
        super().setUp()

    @unittest.skip('manual run only')
    def test_solidity_hello(self):
        _, contract = self.build("solidity_hello")

        def myflow():
            self.deploy(contract)
            answer = self.query_number(contract, "getValue()")
            self.assertEqual(42, answer)

        self.environment.run_flow(myflow)

    @unittest.skip('manual run only')
    def test_solidity_soll_001(self):
        _, contract = self.build("solidity_soll_001")

        def myflow():
            self.deploy(contract)
            answer = add(30, 12)
            self.assertEqual(42, answer)

        def add(a, b):
            args = [a, b]
            return self.query_number(contract, "add(uint256,uint256)", args)

        self.environment.run_flow(myflow)

    @unittest.skip('manual run only')
    def test_solidity_soll_003(self):
        _, contract = self.build("solidity_soll_003")

        def myflow():
            self.deploy(contract, owner=self.alice)

            transfer(self.alice, self.bob, 1000)
            transfer(self.alice, self.carol, 1000)
            self.assertEqual(1000, balance_of(self.bob))
            self.assertEqual(1000, balance_of(self.carol))
            transfer(self.bob, self.carol, 200)
            transfer(self.carol, self.bob, 400)
            self.assertEqual(1200, balance_of(self.bob))
            self.assertEqual(800, balance_of(self.carol))

        def transfer(sender, recipient, amount):
            args = [recipient.address_formatted(), amount]
            self.execute(contract, sender, "transfer(address,uint256)", args)

        def balance_of(account):
            args = [account.address_formatted()]
            return self.query_number(contract, "balanceOf(address)", args)

        self.environment.run_flow(myflow)
