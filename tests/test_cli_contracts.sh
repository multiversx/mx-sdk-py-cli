#!/usr/bin/env bash

source "./shared.sh"

testTrivialCommands() {
    ${ERDPY} contract templates
}

testCreateContracts() {
    ${ERDPY} contract new --template ultimate-answer --directory ${SANDBOX} myanswer
    ${ERDPY} contract new --template adder --directory ${SANDBOX} myadder
    ${ERDPY} contract new --template factorial --directory ${SANDBOX} myfactorial
    ${ERDPY} contract new --template simple-erc20 --directory ${SANDBOX} mytoken
    ${ERDPY} contract new --template crypto-bubbles --directory ${SANDBOX} mybubbles

    # BUSD contract isn't yet migrated to elrond-wasm 0.6.0
    # git clone --depth=1 --branch=master https://github.com/ElrondNetwork/sc-busd-rs.git ${SANDBOX}/sc-busd-rs
    # rm -rf ${SANDBOX}/sc-busd-rs/.git
}

testBuildContracts() {
    ${ERDPY} contract build ${SANDBOX}/myanswer
    ${ERDPY} contract build ${SANDBOX}/myadder
    ${ERDPY} contract build ${SANDBOX}/myfactorial
    ${ERDPY} contract build ${SANDBOX}/mytoken
    ${ERDPY} contract build ${SANDBOX}/mybubbles
    ${ERDPY} contract build ${SANDBOX}/sc-busd-rs
}

testRunMandos() {
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/myadder
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/mytoken
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/mybubbles
}

testAll() {
    cleanSandbox
    testTrivialCommands
    testCreateContracts
    testBuildContracts
    testRunMandos
}
