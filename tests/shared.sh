export PYTHONPATH=../../

ERDPY="python3 -m erdpy.cli"
SANDBOX=testdata-out/SANDBOX
KEYS=../../examples/keys
DENOMINATION="000000000000000000"
PROXY="https://api.elrond.com"
CHAIN_ID="v1.0.147"

cleanSandbox() {
    rm -rf ${SANDBOX}
}

assertFileExists() {
    if [ ! -f "$1" ]
    then
        echo "Error: file [$1] does not exist!" 1>&2
    fi
}