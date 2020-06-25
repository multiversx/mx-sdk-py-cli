#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    BOB="erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"

    ${ERDPY} --verbose tx-prepare-and-send --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --proxy=${PROXY}
    ${ERDPY} --verbose tx-prepare-and-send --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --nonce=42 --gas-limit=50000 --proxy=${PROXY}
    ${ERDPY} --verbose tx-prepare-and-send --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --nonce=43 --gas-limit=60000 --data="foo" --proxy=${PROXY}

    ${ERDPY} --verbose tx-prepare ${SANDBOX} --tag="foobar" --pem="${KEYS}/alice.pem" --nonce=42 --receiver=${BOB} --value="1${DENOMINATION}" --gas-limit=50000
    assertFileExists ${SANDBOX}/tx-foobar.json
    ${ERDPY} --verbose tx-send ${SANDBOX}/tx-foobar.json --proxy=${PROXY}
}
