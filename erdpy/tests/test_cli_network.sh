#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    echo "network.num-shards"
    ${CLI} --verbose network num-shards --proxy=${PROXY}
    echo "network.block-nonce"
    ${CLI} --verbose network block-nonce --shard=0 --proxy=${PROXY}
    echo "network.chain"
    ${CLI} --verbose network chain --proxy=${PROXY}
}
