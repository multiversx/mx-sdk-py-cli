#!/usr/bin/env bash

source "./shared.sh"

testAll() {
    testGeneration || return 1
    testBech32 || return 1
}

testGeneration() {
    echo "testGeneration"
    ${CLI} wallet derive ./testdata-out/myaccount.pem || return 1
    assertFileExists "./testdata-out/myaccount.pem" || return 1
    echo "foo bar\n" | ${CLI} wallet derive --mnemonic ./testdata-out/myaccount-from-mnemonic.pem || return 1
    assertFileExists "./testdata-out/myaccount-from-mnemonic.pem" || return 1
}

testBech32() {
    echo "testBech32"
    ${CLI} wallet bech32 --encode 000000000000000005006e4f90488e27342f9a46e1809452c85ee7186566bd5e || return 1
    ${CLI} wallet bech32 --decode erd1qqqqqqqqqqqqqpgqde8eqjywyu6zlxjxuxqfg5kgtmn3setxh40qen8egy || return 1
}
