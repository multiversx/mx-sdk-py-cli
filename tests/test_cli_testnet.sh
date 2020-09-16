#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    pushd .

    cleanSandbox
    mkdir -p ${SANDBOX}/testnet_foo

    ${ERDPY} testnet prerequisites
    
    cp ./testdata/testnets/testnet_foo.toml ${SANDBOX}/testnet_foo/testnet.toml
    cd ${SANDBOX}/testnet_foo
    ${ERDPY} --verbose testnet config
    ${ERDPY} --verbose testnet start

    popd
}
