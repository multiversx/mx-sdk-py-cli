#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    set -x

    ${CLI} --verbose deps install rust
    ${CLI} --verbose deps install clang
    ${CLI} --verbose deps install vmtools --overwrite

    ${CLI} --verbose deps check rust
    ${CLI} --verbose deps check clang
    ${CLI} --verbose deps check vmtools

    set +x
}
