#!/usr/bin/env bash

source "./shared.sh"

testStart() {
    pushd .

    cleanSandbox
    mkdir -p ${SANDBOX}/testnet_foo

    ${ERDPY} config set dependencies.elrond_proxy_go.tag fix-node-ref
    ${ERDPY} testnet prerequisites
    
    cp ./testdata/testnets/testnet_foo.toml ${SANDBOX}/testnet_foo/testnet.toml
    cd ${SANDBOX}/testnet_foo
    ${ERDPY} --verbose testnet config
    #${ERDPY} --verbose testnet start

    popd
}

testRestart() {
    pushd .

    cleanSandbox
    mkdir -p ${SANDBOX}/testnet_foo

    ${ERDPY} testnet prerequisites
    
    cp ./testdata/testnets/testnet_foo.toml ${SANDBOX}/testnet_foo/testnet.toml
    cd ${SANDBOX}/testnet_foo
    ${ERDPY} --verbose testnet config
    ${ERDPY} --verbose testnet start
    ${ERDPY} --verbose testnet start

    popd
}
