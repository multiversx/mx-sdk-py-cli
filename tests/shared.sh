export PYTHONPATH=$(realpath ../../)
echo "PYTHONPATH = ${PYTHONPATH}"

ERDPY="python3 -m erdpy.cli"
SANDBOX=testdata-out/SANDBOX
KEYS=../../examples/keys
DENOMINATION="000000000000000000"
PROXY="https://api-testnet.elrond.com"
CHAIN_ID="T"

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