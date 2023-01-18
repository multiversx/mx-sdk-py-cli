#!/usr/bin/env bash

source "./shared.sh"

testStart() {
    pushd .

    cleanSandbox
    mkdir -p ${SANDBOX}/testnet_foo

    ${CLI} config set dependencies.mx_chain_proxy_go.tag fix-node-ref
    ${CLI} testnet prerequisites
    
    cp ./testdata/testnets/testnet_foo.toml ${SANDBOX}/testnet_foo/testnet.toml
    cd ${SANDBOX}/testnet_foo
    ${CLI} --verbose testnet config
    ${CLI} --verbose testnet start

    popd
}

testRestart() {
    pushd .

    cleanSandbox
    mkdir -p ${SANDBOX}/testnet_foo

    ${CLI} testnet prerequisites
    
    cp ./testdata/testnets/testnet_foo.toml ${SANDBOX}/testnet_foo/testnet.toml
    cd ${SANDBOX}/testnet_foo
    ${CLI} --verbose testnet config
    ${CLI} --verbose testnet start
    ${CLI} --verbose testnet start

    popd
}
