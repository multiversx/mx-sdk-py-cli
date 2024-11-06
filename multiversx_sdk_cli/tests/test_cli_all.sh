#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
USE_PROXY=$1

source ./shared.sh
source ./test_cli_validators.sh && testAll

testAll() {
    pushd $SCRIPT_DIR
    source ./shared.sh

    if [ -n "$USE_PROXY" ]; then
        source ./test_cli_config.sh && testAll
    fi
    popd
}
