#!/usr/bin/env bash

source "./shared.sh"

testTrivialCommands() {
    ${ERDPY} contract templates
}

testCreateContracts() {
    ${ERDPY} contract new --template ultimate-answer --directory ${SANDBOX} myanswer
    ${ERDPY} contract new --template adder --directory ${SANDBOX} myadder

    git clone --depth=1 --branch=master https://github.com/ElrondNetwork/sc-busd-rs.git ${SANDBOX}/sc-busd-rs
    rm -rf ${SANDBOX}/sc-busd-rs/.git
}

testBuildContracts() {
    ${ERDPY} contract build ${SANDBOX}/myanswer
    ${ERDPY} contract build ${SANDBOX}/myadder
    #${ERDPY} contract build ${SANDBOX}/sc-busd-rs
}

testRunMandos() {
    ${ERDPY} --verbose contract test --directory="test" ${SANDBOX}/myadder
    #${ERDPY} --verbose contract test --directory="tests" ${SANDBOX}/sc-busd-rs
}

testContracts() {
    set -x

    cleanSandbox
    testTrivialCommands
    testCreateContracts
    testBuildContracts
    testRunMandos

    set +x
}
