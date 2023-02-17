#!/usr/bin/env bash

source "./shared.sh"

BOB="erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r"

testAll() {
    cleanSandbox || return 1
    
    echo "tx new, don't --send"
    ${CLI} --verbose tx new --pem="${USERS}/alice.pem" --receiver=${BOB} --value="1${DENOMINATION}" --recall-nonce --data="foo" --gas-limit=70000 --chain=${CHAIN_ID} --outfile=${SANDBOX}/txA.txt || return 1
    echo "tx send"
    ${CLI} --verbose tx send --infile=${SANDBOX}/txA.txt --proxy=${PROXY} || return 1
    echo "tx new --send"
    ${CLI} --verbose tx new --pem="${USERS}/bob.pem" --receiver=${BOB} --value="1${DENOMINATION}" --recall-nonce --data="foo" --gas-limit=60000 --chain=${CHAIN_ID} --send --outfile=${SANDBOX}/txB.txt --proxy=${PROXY} || return 1
    echo "tx new with --data-file"
    echo '"{hello world!}"' > ${SANDBOX}/dummy.txt
    ${CLI} --verbose tx new --pem="${USERS}/carol.pem" --receiver=${BOB} --value="1${DENOMINATION}" --recall-nonce --data-file=${SANDBOX}/dummy.txt --gas-limit=70000 --chain=${CHAIN_ID} --proxy=${PROXY} || return 1

    echo "tx new --relay"
    ${CLI} --verbose tx new --pem="${USERS}/dan.pem" --receiver=${BOB} --value="1${DENOMINATION}" --nonce=1 --data="foo" --gas-limit=70000 --chain=${CHAIN_ID} --outfile=${SANDBOX}/txInner.txt --relay || return 1
    ${CLI} --verbose tx new --pem="${USERS}/eve.pem" --receiver=${BOB} --value="1${DENOMINATION}" --recall-nonce --data-file=${SANDBOX}/txInner.txt --gas-limit=200000 --chain=${CHAIN_ID} --outfile=${SANDBOX}/txWrapper.txt || return 1

    echo "tx new --simulate"
    ${CLI} --verbose tx new --simulate --pem="${USERS}/frank.pem" --receiver=${BOB} --value="1${DENOMINATION}" --recall-nonce --data="foo" --gas-limit=70000 --chain=${CHAIN_ID} --proxy=${PROXY} || return 1

    echo "tx new --send --wait-result"
    ${CLI} --verbose tx new --send --wait-result --pem="${USERS}/grace.pem" --receiver=${BOB} --value="1${DENOMINATION}" --recall-nonce --data="foo" --gas-limit=70000 --chain=${CHAIN_ID} --proxy=${PROXY} || return 1
}
