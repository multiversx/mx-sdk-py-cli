#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    BLS_KEY="b617d8bc442bda59510f77e04a1680e8b2d3293c8c4083d94260db96a4d732deaaf9855fa0cef2273f5a67b4f442c725efc06a5d366b9f15a66da9eb8208a09c9ab4066b6b3d38c3cf1ea7fab6489a90713b3b56d87de68c6558c80d7533bf27"
    REWARD_ADDRESS="erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"

    ${ERDPY} --verbose validator stake --pem="${KEYS}/alice.pem" --value="2500000${DENOMINATION}" --number-of-nodes=1 --nodes-public-keys=${BLS_KEY} --reward-address=${REWARD_ADDRESS} --proxy=${PROXY} --estimate-gas --recall-nonce
    ${ERDPY} --verbose validator stake --pem="${KEYS}/alice.pem" --value="2500000${DENOMINATION}" --number-of-nodes=1 --nodes-public-keys=${BLS_KEY} --reward-address=${REWARD_ADDRESS} --proxy=${PROXY} --estimate-gas --nonce=42

    ${ERDPY} --verbose validator unstake --pem="${KEYS}/alice.pem" --nodes-public-keys=${BLS_KEY} --proxy=${PROXY} --estimate-gas --recall-nonce
    ${ERDPY} --verbose validator unbond --pem="${KEYS}/alice.pem" --nodes-public-keys=${BLS_KEY} --proxy=${PROXY} --estimate-gas --recall-nonce
    ${ERDPY} --verbose validator unjail --pem="${KEYS}/alice.pem" --value="2500${DENOMINATION}" --nodes-public-keys=${BLS_KEY} --proxy=${PROXY} --estimate-gas --recall-nonce
    ${ERDPY} --verbose validator change-reward-address --pem="${KEYS}/alice.pem" --reward-address=${REWARD_ADDRESS} --proxy=${PROXY} --estimate-gas --recall-nonce
}
