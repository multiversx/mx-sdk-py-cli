#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    ${ERDPY} --verbose cost gas-price --proxy=${PROXY}
    ${ERDPY} --verbose cost transaction move-balance --data="foobar" --proxy=${PROXY}
}
