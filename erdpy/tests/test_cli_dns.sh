#!/usr/bin/env bash

source "./shared.sh"

ALICE="${USERS}/alice.pem"
BOB="${USERS}/bob.pem"
BOB_ADDRESS=$(${ERDPY} wallet pem-address ${BOB})
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
        --outfile=${SANDBOX}/txRegisterAlice.txt --send --proxy=${PROXY} || return 1

    ${ERDPY} --verbose dns register --name="bobbysmith" --pem=${BOB} --value=${REGISTRATION_COST} \
        --recall-nonce --gas-limit=100000000 --gas-price=1000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txRegisterBob.txt --send --proxy=${PROXY} || return 1
}

testTransactionsWithUsernamesOnline() {
    ${ERDPY} --verbose tx new --pem=${ALICE} --receiver=${BOB_ADDRESS} \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txA.txt --send --proxy=${PROXY} || return 1

    sleep 10

    ${ERDPY} --verbose tx new --pem=${ALICE} --receiver=${BOB_ADDRESS} --receiver-username="bobbysmith" \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txB.txt --send --proxy=${PROXY} || return 1

    sleep 10

    ${ERDPY} --verbose tx new --pem=${ALICE} --receiver=${BOB_ADDRESS} --receiver-username="bobbysmithfoo" \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txC.txt --send --proxy=${PROXY} || return 1

    sleep 10

    ${ERDPY} --verbose tx new --pem=${ALICE} --sender-username="alicesmith" --receiver=${BOB_ADDRESS} --receiver-username="bobbysmith" \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txD.txt --send --proxy=${PROXY} || return 1

    sleep 10

    ${ERDPY} --verbose tx new --pem=${ALICE} --sender-username="alicesmith" --receiver=${BOB_ADDRESS} \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txF.txt --send --proxy=${PROXY} || return 1

    sleep 10

    ${ERDPY} --verbose tx new --pem=${ALICE} --sender-username="alicesmithfoo" --receiver=${BOB_ADDRESS} \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txG.txt --send --proxy=${PROXY} || return 1
}


testOffline() {
    testRegistrationOffline || return 1
    testTransactionsWithUsernamesOffline || return 1
}

testRegistrationOffline() {
    ${ERDPY} --verbose dns register --name="alicesmith" --pem=${ALICE} --value=${REGISTRATION_COST} \
        --nonce=7 --gas-limit=100000000 --gas-price=1000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txRegisterAlice.txt || return 1
    assertFileExists ${SANDBOX}/txRegisterAlice.txt || return 1

    ${ERDPY} --verbose dns register --name="bobbysmith" --pem=${BOB} --value=${REGISTRATION_COST} \
        --nonce=8 --gas-limit=100000000 --gas-price=1000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txRegisterBob.txt || return 1
    assertFileExists ${SANDBOX}/txRegisterBob.txt || return 1
}

testTransactionsWithUsernamesOffline() {
    ${ERDPY} --verbose tx new --pem=${ALICE} --receiver=${BOB_ADDRESS} \
        --value="1${DENOMINATION}" --nonce=42 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txA.txt || return 1
    assertFileExists ${SANDBOX}/txA.txt || return 1

    ${ERDPY} --verbose tx new --pem=${ALICE} --receiver=${BOB_ADDRESS} --receiver-username="bobbysmith" \
        --value="1${DENOMINATION}" --nonce=43 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txB.txt || return 1
    assertFileExists ${SANDBOX}/txB.txt || return 1

    ${ERDPY} --verbose tx new --pem=${ALICE} --receiver=${BOB_ADDRESS} --receiver-username="bobbysmithfoo" \
        --value="1${DENOMINATION}" --nonce=44 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txC.txt || return 1
    assertFileExists ${SANDBOX}/txC.txt || return 1

    ${ERDPY} --verbose tx new --pem=${ALICE} --sender-username="alicesmith" --receiver=${BOB_ADDRESS} --receiver-username="bobbysmith" \
        --value="1${DENOMINATION}" --nonce=45 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txD.txt || return 1
    assertFileExists ${SANDBOX}/txD.txt || return 1

    ${ERDPY} --verbose tx new --pem=${ALICE} --sender-username="alicesmith" --receiver=${BOB_ADDRESS} \
        --value="1${DENOMINATION}" --nonce=46 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txF.txt || return 1
    assertFileExists ${SANDBOX}/txF.txt || return 1

    ${ERDPY} --verbose tx new --pem=${ALICE} --sender-username="alicesmithfoo" --receiver=${BOB_ADDRESS} \
        --value="1${DENOMINATION}" --nonce=47 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txG.txt || return 1
    assertFileExists ${SANDBOX}/txG.txt || return 1
}

testAll() {
    testOnline || return 1
    testOffline || return 1
}
