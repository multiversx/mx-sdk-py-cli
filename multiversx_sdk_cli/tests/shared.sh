# compatibility with MacOS ( https://stackoverflow.com/a/9484017 )
function absolute_path() {
  DIR="${1%/*}"
  (cd "$DIR" && echo "$(pwd -P)")
}

export PYTHONPATH=$(absolute_path ../../)
echo "PYTHONPATH = ${PYTHONPATH}"

CLI="python3 -m multiversx_sdk_cli.cli"
SANDBOX=./testdata-out/SANDBOX
USERS=~/multiversx-sdk/testwallets/latest/users
VALIDATORS=~/multiversx-sdk/testwallets/latest/validators
DENOMINATION="000000000000000000"
PROXY="${PROXY:-http://localhost:7950}"
CHAIN_ID="${CHAIN_ID:-localnet}"
TestUser=./testdata/testUser.pem
TestUser2=./testdata/testUser2.pem
RUST_VERSION="nightly-2023-04-24"

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
