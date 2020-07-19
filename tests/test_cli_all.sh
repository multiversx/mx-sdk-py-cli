#!/usr/bin/env bash

source "./shared.sh"

runAllTests() {
    source ./tests.sh && runShortTests
    source ./test_cli_wallet.sh && testAll
    source ./test_cli_contracts.sh && testContracts
    source ./test_cli_validators.sh && testAll
    source ./test_cli_tx.sh && testNewApi
    source ./test_cli_config.sh && testAll
    source ./test_cli_network.sh && testAll
    source ./test_cli_cost.sh && testAll
}

runHighImportanceTests() {
    source ./test_cli_validators.sh && testAll
    source ./test_cli_tx.sh && testNewApi
}
