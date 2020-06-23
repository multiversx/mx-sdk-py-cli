#!/usr/bin/env bash

source "./shared.sh"

runShortTests() {
	python3 -m unittest -v erdpy.tests.test_wallet
	python3 -m unittest -v erdpy.tests.test_accounts
	python3 -m unittest -v erdpy.tests.test_contracts
}
