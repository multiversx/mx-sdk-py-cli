#!/usr/bin/env bash

source "./shared.sh"

ALICE="${USERS}/alice.pem"
BOB="${USERS}/bob.pem"
BOB_ADDRESS="erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
REGISTRATION_COST=100

testOnline() {
    testRegistrationOnline || return 1
    # Wait for nonces to be incremented (at source shards)
    sleep 15
    testTransactionsWithUsernamesOnline || return 1
}

testRegistrationOnline() {
    ${ERDPY} --verbose dns register --name="alicesmith" --pem=${ALICE} --value=${REGISTRATION_COST} \
        --recall-nonce --gas-limit=100000000 --gas-price=1000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txRegister.txt --send --proxy=${PROXY} || return 1

    ${ERDPY} --verbose dns register --name="bobbysmith" --pem=${BOB} --value=${REGISTRATION_COST} \
        --recall-nonce --gas-limit=100000000 --gas-price=1000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txRegister.txt --send --proxy=${PROXY} || return 1
}

testTransactionsWithUsernamesOnline() {
    ${ERDPY} --verbose tx new --pem=${ALICE} --receiver=${BOB_ADDRESS} --receiver-username="bobbysmith" \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txA.txt --send --proxy=${PROXY} || return 1
}
