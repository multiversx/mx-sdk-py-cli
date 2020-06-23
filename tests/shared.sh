export PYTHONPATH=../../

ERDPY="python3 -m erdpy.cli"
SANDBOX=testdata-out/SANDBOX

cleanSandbox() {
    rm -rf ${SANDBOX}
}

assertFileExists() {
    if [ ! -f "$1" ]
    then
        echo "Error: file [$1] does not exist!" 1>&2
    fi
}