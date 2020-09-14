#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    echo "network.num-shards"
    ${ERDPY} --verbose network num-shards --proxy=${PROXY}
    echo "network.block-nonce"
    ${ERDPY} --verbose network block-nonce --shard=0 --proxy=${PROXY}
    echo "network.chain"
    ${ERDPY} --verbose network chain --proxy=${PROXY}
}
