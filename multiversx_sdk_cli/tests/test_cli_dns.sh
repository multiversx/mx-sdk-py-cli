#!/usr/bin/env bash

source "./shared.sh"

REGISTRATION_COST=100

testOnline() {
    testRegistrationOnline || return 1
    # Wait for nonces to be incremented (at source shards)
    sleep 15
    testTransactionsWithUsernamesOnline || return 1
}

testRegistrationOnline() {
    ${CLI} --verbose dns register --name="testuser" --pem=${TestUser} --value=${REGISTRATION_COST} \
        --recall-nonce --gas-limit=100000000 --gas-price=1000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txRegisterUser.txt --send --proxy=${PROXY} || return 1

    ${CLI} --verbose dns register --name="testuser2" --pem=${TestUser2} --value=${REGISTRATION_COST} \
        --recall-nonce --gas-limit=100000000 --gas-price=1000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txRegisterUser2.txt --send --proxy=${PROXY} || return 1
}

testTransactionsWithUsernamesOnline() {
    ${CLI} --verbose tx new --pem=${TestUser} --receiver=${TestUser2} \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txA.txt --send --proxy=${PROXY} || return 1

    sleep 10

    ${CLI} --verbose tx new --pem=${TestUser} --receiver=${TestUser2} --receiver-username="testuser2" \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txB.txt --send --proxy=${PROXY} || return 1

    sleep 10

    ${CLI} --verbose tx new --pem=${TestUser} --receiver=${TestUser2} --receiver-username="testuser2foo" \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txC.txt --send --proxy=${PROXY} || return 1

    sleep 10

    ${CLI} --verbose tx new --pem=${TestUser} --sender-username="testuser" --receiver=${TestUser2} --receiver-username="testuser2" \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txD.txt --send --proxy=${PROXY} || return 1

    sleep 10

    ${CLI} --verbose tx new --pem=${TestUser} --sender-username="testuser" --receiver=${TestUser2} \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txF.txt --send --proxy=${PROXY} || return 1

    sleep 10

    ${CLI} --verbose tx new --pem=${TestUser} --sender-username="testuserfoo" --receiver=${TestUser2} \
        --value="1${DENOMINATION}" --recall-nonce --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txG.txt --send --proxy=${PROXY} || return 1
}


testOffline() {
    testRegistrationOffline || return 1
    testTransactionsWithUsernamesOffline || return 1
}

testRegistrationOffline() {
    ${CLI} --verbose dns register --name="testuser" --pem=${TestUser} --value=${REGISTRATION_COST} \
        --nonce=7 --gas-limit=100000000 --gas-price=1000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txRegisterUser.txt || return 1
    assertFileExists ${SANDBOX}/txRegisterUser.txt || return 1

    ${CLI} --verbose dns register --name="testuser2" --pem=${TestUser2} --value=${REGISTRATION_COST} \
        --nonce=8 --gas-limit=100000000 --gas-price=1000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txRegisterUser2.txt || return 1
    assertFileExists ${SANDBOX}/txRegisterUser2.txt || return 1
}

testTransactionsWithUsernamesOffline() {
    ${CLI} --verbose tx new --pem=${TestUser} --receiver="erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4" \
        --value="1${DENOMINATION}" --nonce=42 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txA.txt || return 1
    assertFileExists ${SANDBOX}/txA.txt || return 1

    ${CLI} --verbose tx new --pem=${TestUser} --receiver="erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4" --receiver-username="testuser2" \
        --value="1${DENOMINATION}" --nonce=43 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txB.txt || return 1
    assertFileExists ${SANDBOX}/txB.txt || return 1

    ${CLI} --verbose tx new --pem=${TestUser} --receiver="erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4" --receiver-username="testuser2foo" \
        --value="1${DENOMINATION}" --nonce=44 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txC.txt || return 1
    assertFileExists ${SANDBOX}/txC.txt || return 1

    ${CLI} --verbose tx new --pem=${TestUser} --sender-username="testuser" --receiver="erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4" --receiver-username="testuser2" \
        --value="1${DENOMINATION}" --nonce=45 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txD.txt || return 1
    assertFileExists ${SANDBOX}/txD.txt || return 1

    ${CLI} --verbose tx new --pem=${TestUser} --sender-username="testuser" --receiver="erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4" \
        --value="1${DENOMINATION}" --nonce=46 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txF.txt || return 1
    assertFileExists ${SANDBOX}/txF.txt || return 1

    ${CLI} --verbose tx new --pem=${TestUser} --sender-username="testuserfoo" --receiver="erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4" \
        --value="1${DENOMINATION}" --nonce=47 --gas-limit=50000 --gas-price=2000000000 --chain=${CHAIN_ID} \
        --outfile=${SANDBOX}/txG.txt || return 1
    assertFileExists ${SANDBOX}/txG.txt || return 1
}

testAll() {
    testOnline || return 1
    testOffline || return 1
}
