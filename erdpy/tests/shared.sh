export PYTHONPATH=$(realpath ../../)
echo "PYTHONPATH = ${PYTHONPATH}"

ERDPY="python3 -m erdpy.cli"
SANDBOX=testdata-out/SANDBOX
USERS=../testnet/wallets/users
VALIDATORS=../testnet/wallets/validators
DENOMINATION="000000000000000000"
PROXY="http://localhost:7950"
CHAIN_ID="local-testnet"

cleanSandbox() {
    rm -rf ${SANDBOX}
    mkdir -p ${SANDBOX}
}

assertFileExists() {
    if [ ! -f "$1" ]
    then
        echo "Error: file [$1] does not exist!" 1>&2
        return 1
    fi

    return 0
}

assertFileDoesNotExist() {
    if [ -f "$1" ]
    then
        echo "Error: expected file [$1] to be missing, but it exists!" 1>&2
        return 1
    fi

    return 0
}
