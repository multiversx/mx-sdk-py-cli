#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
USE_PROXY=$1

testAll() {
    pushd $SCRIPT_DIR
    source ./shared.sh
    source ./test_cli_contracts.sh && testAll
    source ./test_cli_wallet.sh && testAll
    source ./test_cli_dns.sh && testAll

    if [ -n "$USE_PROXY" ]; then
        source ./test_cli_validators.sh && testAll
        source ./test_cli_tx.sh && testAll
        source ./test_cli_config.sh && testAll
        source ./test_cli_network.sh && testAll
        source ./test_cli_cost.sh && testAll
    fi
    popd
}
