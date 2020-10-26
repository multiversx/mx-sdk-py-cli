export PYTHONPATH=$(realpath ../../)
echo "PYTHONPATH = ${PYTHONPATH}"

ERDPY="python3 -m erdpy.cli"
SANDBOX=testdata-out/SANDBOX
USERS=../testnet/wallets/users
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
    fi
}