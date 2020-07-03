#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    ${ERDPY} --verbose deps install rust
    ${ERDPY} --verbose deps install clang
    ${ERDPY} --verbose deps install arwentools --overwrite

    ${ERDPY} --verbose deps check rust
    ${ERDPY} --verbose deps check clang
    ${ERDPY} --verbose deps check arwentools --overwrite
}
