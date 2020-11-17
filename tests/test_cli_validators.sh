#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    BLS_KEY="e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    REWARD_ADDRESS="erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"

    echo "Stake with recall nonce"
    ${ERDPY} --verbose validator stake --pem="${USERS}/alice.pem" --value="2500${DENOMINATION}" --validators-file=./testdata/validators.json --reward-address=${REWARD_ADDRESS} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send
    echo "Stake with provided nonce"
    ${ERDPY} --verbose validator stake --pem="${USERS}/alice.pem" --value="2500${DENOMINATION}" --validators-file=./testdata/validators.json --reward-address=${REWARD_ADDRESS} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --nonce=42 --send

    echo "Unstake"
    ${ERDPY} --verbose validator unstake --pem="${USERS}/alice.pem" --nodes-public-keys=${BLS_KEY} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send
    echo "Unbond"
    ${ERDPY} --verbose validator unbond --pem="${USERS}/alice.pem" --nodes-public-keys=${BLS_KEY} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send
    echo "Unjail"
    ${ERDPY} --verbose validator unjail --pem="${USERS}/alice.pem" --value="2500${DENOMINATION}" --nodes-public-keys=${BLS_KEY} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send
    echo "Change reward address"
    ${ERDPY} --verbose validator change-reward-address --pem="${USERS}/alice.pem" --reward-address=${REWARD_ADDRESS} --chain=${CHAIN_ID} --proxy=${PROXY} --estimate-gas --recall-nonce --send
}
