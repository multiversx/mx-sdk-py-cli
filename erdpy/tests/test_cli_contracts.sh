#!/usr/bin/env bash

source "./shared.sh"

testTrivialCommands() {
    echo "testTrivialCommands"
    ${ERDPY} contract templates
}

testCreateContracts() {
    echo "testCreateContracts"
    ${ERDPY} contract new --template ultimate-answer --directory ${SANDBOX} myanswer-c || return 1
    ${ERDPY} contract new --template simple-counter --directory ${SANDBOX} mycounter-c || return 1
    ${ERDPY} contract new --template erc20-c --directory ${SANDBOX} myerc20-c || return 1

    ${ERDPY} contract new --template adder --directory ${SANDBOX} myadder-rs || return 1
    ${ERDPY} contract new --template factorial --directory ${SANDBOX} myfactorial-rs || return 1
    ${ERDPY} contract new --template crypto-bubbles --directory ${SANDBOX} mybubbles-rs || return 1
    ${ERDPY} contract new --template lottery-esdt --directory ${SANDBOX} mylottery-rs || return 1
    ${ERDPY} contract new --template crowdfunding-esdt --directory ${SANDBOX} myfunding-rs || return 1
    ${ERDPY} contract new --template multisig --directory ${SANDBOX} multisig-rs || return 1
}

testBuildContracts() {
    echo "testBuildContracts"
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
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-rs.abi.json || return 1

    ${ERDPY} contract build ${SANDBOX}/myfactorial-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.abi.json || return 1

    ${ERDPY} contract build --ignore-eei-checks ${SANDBOX}/mybubbles-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.wasm || return 1
    assertFileExists ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.abi.json || return 1

    ${ERDPY} contract build --ignore-eei-checks ${SANDBOX}/mylottery-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/mylottery-rs/output/mylottery-rs.wasm || return 1
    assertFileExists ${SANDBOX}/mylottery-rs/output/mylottery-rs.abi.json || return 1

    ${ERDPY} contract build --ignore-eei-checks ${SANDBOX}/myfunding-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/myfunding-rs/output/myfunding-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myfunding-rs/output/myfunding-rs.abi.json || return 1
}

testRunMandos() {
    echo "testRunMandos"
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/myadder-rs || return 1
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/mybubbles-rs || return 1
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/mylottery-rs || return 1
    ${ERDPY} --verbose contract test --directory="mandos" ${SANDBOX}/myfunding-rs || return 1
}

testWasmName() {
    echo "testWasmName"
    ${ERDPY} contract clean ${SANDBOX}/myanswer-c || return 1
    assertFileDoesNotExist ${SANDBOX}/myanswer-c/output/answer-2.wasm || return 1
    ${ERDPY} contract build ${SANDBOX}/myanswer-c --wasm-name answer-2 || return 1
    assertFileExists ${SANDBOX}/myanswer-c/output/answer-2.wasm || return 1

    ${ERDPY} contract clean ${SANDBOX}/myadder-rs
    assertFileDoesNotExist ${SANDBOX}/myadder-rs/output/myadder-2-rs.wasm || return 1
    ${ERDPY} contract build ${SANDBOX}/myadder-rs --cargo-target-dir=${TARGET_DIR} --wasm-name myadder-2-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-2-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-rs.abi.json || return 1
}

testCleanContracts() {
    echo "testCleanContracts"
    assertFileExists ${SANDBOX}/myanswer-c/output/answer.wasm || return 1
    ${ERDPY} contract clean ${SANDBOX}/myanswer-c || return 1
    assertFileDoesNotExist ${SANDBOX}/myanswer-c/output/answer.wasm || return 1

    assertFileExists ${SANDBOX}/mycounter-c/output/counter.wasm || return 1
    ${ERDPY} contract clean ${SANDBOX}/mycounter-c || return 1
    assertFileDoesNotExist ${SANDBOX}/mycounter-c/output/counter.wasm || return 1

    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-rs.abi.json || return 1
    ${ERDPY} contract clean ${SANDBOX}/myadder-rs || return 1
    assertFileDoesNotExist ${SANDBOX}/myadder-rs/output/myadder-rs.wasm || return 1
    assertFileDoesNotExist ${SANDBOX}/myadder-rs/output/myadder-rs.abi.json || return 1

    assertFileExists ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.abi.json || return 1
    ${ERDPY} contract clean ${SANDBOX}/myfactorial-rs || return 1
    assertFileDoesNotExist ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.wasm || return 1
    assertFileDoesNotExist ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.abi.json || return 1

    assertFileExists ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.wasm || return 1
    assertFileExists ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.abi.json || return 1
    ${ERDPY} contract clean ${SANDBOX}/mybubbles-rs || return 1
    assertFileDoesNotExist ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.wasm || return 1
    assertFileDoesNotExist ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.abi.json || return 1

    assertFileExists ${SANDBOX}/mylottery-rs/output/mylottery-rs.wasm || return 1
    assertFileExists ${SANDBOX}/mylottery-rs/output/mylottery-rs.abi.json || return 1
    ${ERDPY} contract clean ${SANDBOX}/mylottery-rs || return 1
    assertFileDoesNotExist ${SANDBOX}/mylottery-rs/output/mylottery-rs.wasm || return 1
    assertFileDoesNotExist ${SANDBOX}/mylottery-rs/output/mylottery-rs.abi.json || return 1

    assertFileExists ${SANDBOX}/myfunding-rs/output/myfunding-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myfunding-rs/output/myfunding-rs.abi.json || return 1
    ${ERDPY} contract clean ${SANDBOX}/myfunding-rs || return 1
    assertFileDoesNotExist ${SANDBOX}/myfunding-rs/output/myfunding-rs.wasm || return 1
    assertFileDoesNotExist ${SANDBOX}/myfunding-rs/output/myfunding-rs.abi.json || return 1
}

testReproducibleBuild(){
    echo "testReproducibleBuild"

    ${ERDPY} contract reproducible-build ${SANDBOX}/ping-pong-smart-contract --contract=ping-pong --docker-image=elrondnetwork/build-contract-rust:v4.0.0
    assertFileExists ${SANDBOX}/ping-pong-smart-contract/output-docker/ping-pong/ping-pong.wasm || return 1
}

testAll() {
    cleanSandbox || return 1
    testTrivialCommands || return 1
    testCreateContracts || return 1
    testBuildContracts || return 1
    testRunMandos || return 1
    testCleanContracts || return 1
    testWasmName || return 1
}
