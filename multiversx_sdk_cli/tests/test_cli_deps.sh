#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    set -x

    ${CLI} --verbose deps install rust --tag=${VERSION_RUST}
    ${CLI} --verbose deps install vmtools --overwrite

    ${CLI} --verbose deps check rust
    ${CLI} --verbose deps check vmtools

    set +x
}
