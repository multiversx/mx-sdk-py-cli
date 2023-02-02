#!/usr/bin/env bash

source "./shared.sh"

testTrivialCommands() {
    echo "testTrivialCommands"
    ${CLI} contract templates
}

testCreateContracts() {
    echo "testCreateContracts"
    ${CLI} contract new --template ultimate-answer --directory ${SANDBOX} myanswer-c || return 1
    ${CLI} contract new --template simple-counter --directory ${SANDBOX} mycounter-c || return 1
    ${CLI} contract new --template erc20-c --directory ${SANDBOX} myerc20-c || return 1

    ${CLI} contract new --template adder --directory ${SANDBOX} myadder-rs || return 1
    ${CLI} contract new --template factorial --directory ${SANDBOX} myfactorial-rs || return 1
    ${CLI} contract new --template crypto-bubbles --directory ${SANDBOX} mybubbles-rs || return 1
    ${CLI} contract new --template lottery-esdt --directory ${SANDBOX} mylottery-rs || return 1
    ${CLI} contract new --template crowdfunding-esdt --directory ${SANDBOX} myfunding-rs || return 1
    ${CLI} contract new --template multisig --directory ${SANDBOX} multisig-rs || return 1
}

testBuildContracts() {
    echo "testBuildContracts"
    ${CLI} contract build ${SANDBOX}/myanswer-c || return 1
    assertFileExists ${SANDBOX}/myanswer-c/output/answer.wasm || return 1

    ${CLI} contract build ${SANDBOX}/mycounter-c || return 1
    assertFileExists ${SANDBOX}/mycounter-c/output/counter.wasm || return 1

    ${CLI} contract build ${SANDBOX}/myerc20-c || return 1
    assertFileExists ${SANDBOX}/myerc20-c/output/erc20.wasm || return 1

    # Improve compilation time by reusing build artifacts for Rust projects
    export TARGET_DIR=$(pwd)/${SANDBOX}/TARGET
    mkdir -p ${TARGET_DIR}

    ${CLI} contract build ${SANDBOX}/myadder-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-rs.abi.json || return 1

    ${CLI} contract build ${SANDBOX}/myfactorial-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.abi.json || return 1

    ${CLI} contract build --ignore-eei-checks ${SANDBOX}/mybubbles-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.wasm || return 1
    assertFileExists ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.abi.json || return 1

    ${CLI} contract build --ignore-eei-checks ${SANDBOX}/mylottery-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/mylottery-rs/output/mylottery-rs.wasm || return 1
    assertFileExists ${SANDBOX}/mylottery-rs/output/mylottery-rs.abi.json || return 1

    ${CLI} contract build --ignore-eei-checks ${SANDBOX}/myfunding-rs --cargo-target-dir=${TARGET_DIR} || return 1
    assertFileExists ${SANDBOX}/myfunding-rs/output/myfunding-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myfunding-rs/output/myfunding-rs.abi.json || return 1
}

testRunScenarios() {
    echo "testRunScenarios"
    ${CLI} --verbose contract test --directory="scenarios" ${SANDBOX}/myadder-rs || return 1
    ${CLI} --verbose contract test --directory="scenarios" ${SANDBOX}/mybubbles-rs || return 1
    ${CLI} --verbose contract test --directory="scenarios" ${SANDBOX}/mylottery-rs || return 1
    ${CLI} --verbose contract test --directory="scenarios" --recursive ${SANDBOX}/myfunding-rs || return 1
}

testWasmName() {
    echo "testWasmName"
    ${CLI} contract clean ${SANDBOX}/myanswer-c || return 1
    assertFileDoesNotExist ${SANDBOX}/myanswer-c/output/answer-2.wasm || return 1
    ${CLI} contract build ${SANDBOX}/myanswer-c --wasm-name answer-2 || return 1
    assertFileExists ${SANDBOX}/myanswer-c/output/answer-2.wasm || return 1

    ${CLI} contract clean ${SANDBOX}/myadder-rs
    assertFileDoesNotExist ${SANDBOX}/myadder-rs/output/myadder-2-rs.wasm || return 1
    ${CLI} contract build ${SANDBOX}/myadder-rs --cargo-target-dir=${TARGET_DIR} --wasm-name myadder-2-rs || return 1
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-2-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-rs.abi.json || return 1
}

testCleanContracts() {
    echo "testCleanContracts"
    assertFileExists ${SANDBOX}/myanswer-c/output/answer.wasm || return 1
    ${CLI} contract clean ${SANDBOX}/myanswer-c || return 1
    assertFileDoesNotExist ${SANDBOX}/myanswer-c/output/answer.wasm || return 1

    assertFileExists ${SANDBOX}/mycounter-c/output/counter.wasm || return 1
    ${CLI} contract clean ${SANDBOX}/mycounter-c || return 1
    assertFileDoesNotExist ${SANDBOX}/mycounter-c/output/counter.wasm || return 1

    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myadder-rs/output/myadder-rs.abi.json || return 1
    ${CLI} contract clean ${SANDBOX}/myadder-rs || return 1
    assertFileDoesNotExist ${SANDBOX}/myadder-rs/output/myadder-rs.wasm || return 1
    assertFileDoesNotExist ${SANDBOX}/myadder-rs/output/myadder-rs.abi.json || return 1

    assertFileExists ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.abi.json || return 1
    ${CLI} contract clean ${SANDBOX}/myfactorial-rs || return 1
    assertFileDoesNotExist ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.wasm || return 1
    assertFileDoesNotExist ${SANDBOX}/myfactorial-rs/output/myfactorial-rs.abi.json || return 1

    assertFileExists ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.wasm || return 1
    assertFileExists ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.abi.json || return 1
    ${CLI} contract clean ${SANDBOX}/mybubbles-rs || return 1
    assertFileDoesNotExist ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.wasm || return 1
    assertFileDoesNotExist ${SANDBOX}/mybubbles-rs/output/mybubbles-rs.abi.json || return 1

    assertFileExists ${SANDBOX}/mylottery-rs/output/mylottery-rs.wasm || return 1
    assertFileExists ${SANDBOX}/mylottery-rs/output/mylottery-rs.abi.json || return 1
    ${CLI} contract clean ${SANDBOX}/mylottery-rs || return 1
    assertFileDoesNotExist ${SANDBOX}/mylottery-rs/output/mylottery-rs.wasm || return 1
    assertFileDoesNotExist ${SANDBOX}/mylottery-rs/output/mylottery-rs.abi.json || return 1

    assertFileExists ${SANDBOX}/myfunding-rs/output/myfunding-rs.wasm || return 1
    assertFileExists ${SANDBOX}/myfunding-rs/output/myfunding-rs.abi.json || return 1
    ${CLI} contract clean ${SANDBOX}/myfunding-rs || return 1
    assertFileDoesNotExist ${SANDBOX}/myfunding-rs/output/myfunding-rs.wasm || return 1
    assertFileDoesNotExist ${SANDBOX}/myfunding-rs/output/myfunding-rs.abi.json || return 1
}

testVerifyContract(){
    echo "testVerifyContract"

    nohup python3 local_verify_server.py >/dev/null 2>&1 &
    sleep 1

    query_response=$(curl -s localhost:7777/verify -X POST)

    command_response=$(${CLI} contract verify erd1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qn50nnm \
                        --verifier-url=http://localhost:7777 --packaged-src=testdata/dummy.json \
                        --pem=testdata/walletKey.pem --docker-image=multiversx/sdk-rust-contract-builder:v4.0.0)

    result_curl=$(echo $query_response | awk -F ": " '{ print $2 }' | awk -F'"' '{print $2}')
    result_cli=$(echo $command_response | awk -F ": " '{ print $2 }' | awk -F'"' '{print $2}')

    if [[ $result_curl == $result_cli ]];
    then
        echo "Test passed!"
    else
        return 1
    fi

    pkill -f local_verify_server.py
}

testReproducibleBuild(){
    echo "testReproducibleBuild"

    ${CLI} contract reproducible-build ${SANDBOX}/ping-pong-smart-contract --contract=ping-pong --docker-image=multiversx/sdk-rust-contract-builder:v4.1.2 --no-docker-interactive --no-docker-tty || return 1
    assertFileExists ${SANDBOX}/ping-pong-smart-contract/output-docker/ping-pong/ping-pong.wasm || return 1
}

testAll() {
    cleanSandbox || return 1
    testTrivialCommands || return 1
    testCreateContracts || return 1
    testBuildContracts || return 1
    testReproducibleBuild || return 1
    testRunScenarios || return 1
    testCleanContracts || return 1
    testWasmName || return 1
}
