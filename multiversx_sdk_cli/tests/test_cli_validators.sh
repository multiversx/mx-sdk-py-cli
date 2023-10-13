#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    BLS_KEY="e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    REWARD_ADDRESS="erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"

    echo "Stake with recall nonce"
    ${CLI} --verbose validator stake --pem="${USERS}/alice.pem" --value="2500${DENOMINATION}" --validators-file=./testdata/validators.json --reward-address=${REWARD_ADDRESS} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1
    echo "Stake with provided nonce"
    ${CLI} --verbose validator stake --pem="${USERS}/bob.pem" --value="2500${DENOMINATION}" --validators-file=./testdata/validators.json --reward-address=${REWARD_ADDRESS} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --nonce=300 --send || return 1


    echo "Stake with topUP"
    ${CLI} --verbose validator stake --top-up --pem="${USERS}/carol.pem" --value="2711${DENOMINATION}" --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1

    echo "Unstake"
    ${CLI} --verbose validator unstake --pem="${USERS}/dan.pem" --nodes-public-keys="${BLS_KEY}" --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1
    echo "Unbond"
    ${CLI} --verbose validator unbond --pem="${USERS}/eve.pem" --nodes-public-keys=${BLS_KEY} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1
    echo "Unjail"
    ${CLI} --verbose validator unjail --pem="${USERS}/frank.pem" --value="2500${DENOMINATION}" --nodes-public-keys=${BLS_KEY} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1
    echo "Change reward address"
    ${CLI} --verbose validator change-reward-address --pem="${USERS}/grace.pem" --reward-address=${REWARD_ADDRESS} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1

    echo "UnstakeNodes"
    ${CLI} --verbose validator unstake-nodes --pem="${USERS}/heidi.pem" --nodes-public-keys=${BLS_KEY} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1

    echo "UnstakeTokens"
    ${CLI} --verbose validator unstake-tokens --pem="${USERS}/ivan.pem" --unstake-value="11${DENOMINATION}" --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1

    echo "UnbondNodes"
    ${CLI} --verbose validator unbond-nodes --pem="${USERS}/judy.pem" --nodes-public-keys=${BLS_KEY} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1

    echo "UnbondTokens"
    ${CLI} --verbose validator unbond-tokens --pem="${USERS}/mallory.pem" --unbond-value="20${DENOMINATION}" --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1

    echo "CleanRegistrationData"
    ${CLI} --verbose validator clean-registered-data --pem="${USERS}/mike.pem" --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1

    echo "ReStakeUnstakedNodes"
    ${CLI} --verbose validator restake-unstaked-nodes --pem="${USERS}/alice.pem" --nodes-public-keys=${BLS_KEY} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send || return 1
}
