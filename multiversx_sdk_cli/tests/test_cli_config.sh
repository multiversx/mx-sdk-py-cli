#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    set -x

    ${CLI} --verbose config set proxy "https://testnet-api.multiversx.com"
    ${CLI} --verbose config get proxy
    ${CLI} --verbose config set txVersion 1
    ${CLI} --verbose config get txVersion

    set +x
}
