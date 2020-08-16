#!/usr/bin/env bash

source "./shared.sh"

BOB="erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"

testAll() {
    echo "tx new, don't --send"
    ${ERDPY} --verbose tx new --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --nonce=42 --data="foo" --gas-limit=70000 --chain=${CHAIN_ID} --outfile=${SANDBOX}/tx42.txt
    echo "tx send"
    ${ERDPY} --verbose tx send --infile=${SANDBOX}/tx42.txt
    echo "tx new --send"
    ${ERDPY} --verbose tx new --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --nonce=43 --data="foo" --gas-limit=60000 --chain=${CHAIN_ID} --send --outfile=${SANDBOX}/tx43.txt
    echo "tx new with --data-file"
    echo '"{hello world!}"' > ${SANDBOX}/dummy.txt
    ${ERDPY} --verbose tx new --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --recall-nonce --data-file=${SANDBOX}/dummy.txt --gas-limit=70000 --chain=${CHAIN_ID}

    echo "tx new --relay"
    ${ERDPY} --verbose tx new --pem="${KEYS}/carol.pem" --receiver=${BOB} --value="1${DENOMINATION}" --nonce=1 --data="foo" --gas-limit=70000 --chain=${CHAIN_ID} --outfile=${SANDBOX}/txInner.txt --relay
    ${ERDPY} --verbose tx new --pem="${KEYS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --nonce=44 --data-file=${SANDBOX}/txInner.txt --gas-limit=200000 --chain=${CHAIN_ID} --outfile=${SANDBOX}/txWrapper.txt
}