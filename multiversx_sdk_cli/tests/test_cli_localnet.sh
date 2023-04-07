#!/usr/bin/env bash

source "./shared.sh"

testStartThenStop() {
    pushd .

    cleanSandbox
    mkdir -p ${SANDBOX}/localnet_foo
    cp ./testdata/localnet.toml ${SANDBOX}/localnet_foo/localnet.toml
    cd ${SANDBOX}/localnet_foo

    ${CLI} localnet prerequisites
    ${CLI} localnet build
    ${CLI} localnet config

    # Leave the localnet to run for some time, then assert for "time out error" (124).
    timeout 1m ${CLI} localnet start || \
    test $? -eq 124 || \
    echo "Timeout error expected, but something else happened."

    popd
}
