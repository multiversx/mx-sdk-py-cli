#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
USE_PROXY=$1

testAll() {
    pushd $SCRIPT_DIR
    source ./shared.sh

    if [ -n "$USE_PROXY" ]; then
        source ./test_cli_config.sh && testAll
    fi
    popd
}
