#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    ${ERDPY} --verbose network num-shards --proxy=${PROXY}
    ${ERDPY} --verbose network block-nonce --shard=0 --proxy=${PROXY}
    ${ERDPY} --verbose network chain --proxy=${PROXY}
}
