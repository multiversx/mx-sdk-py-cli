#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    set -x

    ${ERDPY} --verbose config set proxy "https://testnet-api.elrond.com"
    ${ERDPY} --verbose config get proxy
    ${ERDPY} --verbose config set txVersion 1
    ${ERDPY} --verbose config get txVersion

    set +x
}
