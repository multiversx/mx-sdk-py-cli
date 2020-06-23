#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    ${ERDPY} --verbose install rust
    ${ERDPY} --verbose install clang
    ${ERDPY} --verbose install arwentools --overwrite
}
