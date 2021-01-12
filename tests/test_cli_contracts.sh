#!/usr/bin/env bash

source "./shared.sh"

testTrivialCommands() {
    ${ERDPY} contract templates
}

testCreateContracts() {
    ${ERDPY} contract new --template ultimate-answer --directory ${SANDBOX} myanswer-c || return 1
    ${ERDPY} contract new --template simple-counter --directory ${SANDBOX} mycounter-c || return 1
    ${ERDPY} contract new --template erc20-c --directory ${SANDBOX} myerc20-c || return 1

    ${ERDPY} contract new --template adder --directory ${SANDBOX} myadder-rs || return 1
    ${ERDPY} contract new --template factorial --directory ${SANDBOX} myfactorial-rs || return 1
    ${ERDPY} contract new --template simple-erc20 --directory ${SANDBOX} myerc20-rs || return 1
    ${ERDPY} contract new --template crypto-bubbles --directory ${SANDBOX} mybubbles-rs || return 1
    ${ERDPY} contract new --template lottery-egld --directory ${SANDBOX} mylottery-rs || return 1
    ${ERDPY} contract new --template crowdfunding-egld --directory ${SANDBOX} myfunding-rs || return 1
}

testBuildContracts() {
    ${ERDPY} contract build ${SANDBOX}/myanswer-c || return 1
    assertFileExists ${SANDBOX}/myanswer-c/output/answer.wasm || return 1

    ${ERDPY} contract build ${SANDBOX}/mycounter-c || return 1
    assertFileExists ${SANDBOX}/mycounter-c/output/counter.wasm || return 1

    ${ERDPY} contract build ${SANDBOX}/myerc20-c || return 1
    assertFileExists ${SANDBOX}/myerc20-c/output/erc20.wasm || return 1
        
    # Improve compilation time by reusing build artifacts for Rust projects
    export TARGET_DIR=$(pwd)/${SANDBOX}/TARGET
    mkdir -p ${TARGET_DIR}

    ${ERDPY} contract build ${SANDBOX}/myadder-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder_rs.wasm || return 1
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder_rs.abi.json || return 1

    ${ERDPY} contract build ${SANDBOX}/myfactorial-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/myfactorial-rs/output/myfactorial_rs.wasm || return 1
    assertFileExists ${SANDBOX}/myfactorial-rs/output/myfactorial_rs.abi.json || return 1

    ${ERDPY} contract build ${SANDBOX}/myerc20-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/myerc20-rs/output/myerc20_rs.wasm || return 1
    assertFileExists ${SANDBOX}/myerc20-rs/output/myerc20_rs.abi.json || return 1
    
    ${ERDPY} contract build ${SANDBOX}/mybubbles-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/mybubbles-rs/output/mybubbles_rs.wasm || return 1
    assertFileExists ${SANDBOX}/mybubbles-rs/output/mybubbles_rs.abi.json || return 1

    ${ERDPY} contract build ${SANDBOX}/mylottery-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/mylottery-rs/output/mylottery_rs.wasm || return 1
    assertFileExists ${SANDBOX}/mylottery-rs/output/mylottery_rs.abi.json || return 1

    ${ERDPY} contract build ${SANDBOX}/myfunding-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/myfunding-rs/output/myfunding_rs.wasm || return 1
    assertFileExists ${SANDBOX}/myfunding-rs/output/myfunding_rs.abi.json || return 1
}

testRunMandos() {
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/myadder-rs || return 1
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/myfactorial-rs || return 1
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/myerc20-rs || return 1
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/mybubbles-rs || return 1
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/mylottery-rs || return 1
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/myfunding-rs || return 1
}

testAll() {
    cleanSandbox || return 1
    testTrivialCommands || return 1
    testCreateContracts || return 1
    testBuildContracts || return 1
    testRunMandos || return 1
}
