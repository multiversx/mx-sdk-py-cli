#!/usr/bin/env bash

source "./shared.sh"

BOB="erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"

testAll() {
    ${ERDPY} --verbose tx-prepare-and-send --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --proxy=${PROXY}
    ${ERDPY} --verbose tx-prepare-and-send --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --nonce=42 --gas-limit=50000 --proxy=${PROXY}
    ${ERDPY} --verbose tx-prepare-and-send --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --nonce=43 --gas-limit=60000 --data="foo" --proxy=${PROXY}

    ${ERDPY} --verbose tx-prepare ${SANDBOX} --tag="foobar" --pem="${KEYS}/alice.pem" --nonce=42 --receiver=${BOB} --value="1${DENOMINATION}" --gas-limit=50000
    assertFileExists ${SANDBOX}/tx-foobar.json
    ${ERDPY} --verbose tx-send ${SANDBOX}/tx-foobar.json --proxy=${PROXY}
}

testNewApi() {
    ${ERDPY} --verbose tx new --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --nonce=42 --data="foo" --gas-limit=70000 --outfile=${SANDBOX}/tx42.txt
    ${ERDPY} --verbose tx send --infile=${SANDBOX}/tx42.txt
    ${ERDPY} --verbose tx new --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --nonce=43 --data="foo" --gas-limit=60000 --send --outfile=${SANDBOX}/tx43.txt
    echo '"{hello world!}"' > ${SANDBOX}/dummy.txt
    ${ERDPY} --verbose tx new --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --recall-nonce --data-file=${SANDBOX}/dummy.txt --gas-limit=70000
}