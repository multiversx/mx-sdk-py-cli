#!/usr/bin/env bash

export PYTHONPATH=../

ERDPY="python3 -m erdpy.cli"

code() {
    printf "\n\`\`\`\n" >> CLI.md
}

group() {
    printf "## Group **$1**\n\n" >> CLI.md

    code
    printf "$ erdpy $2 --help\n" >> CLI.md
    ${ERDPY} ${2} --help >> CLI.md
    code
}

command() {
    printf "### $1\n\n" >> CLI.md

    code
    printf "$ erdpy $2 --help\n" >> CLI.md
    ${ERDPY} ${2} --help >> CLI.md
    code
}

generate() {
    echo -n > CLI.md
    printf "# Command Line Interface\n\n" >> CLI.md

    printf "## Overview\n\n" >> CLI.md
    printf "**erdpy** exposes a number of CLI **commands**, organized within **groups**.\n\n" >> CLI.md

    code
    printf "$ erdpy --help\n" >> CLI.md
    ${ERDPY} --help >> CLI.md
    code

    group "Contract" "contract"
    command "Contract.New" "contract new"
    command "Contract.Templates" "contract templates"
    command "Contract.Build" "contract build"
    command "Contract.Clean" "contract clean"
    command "Contract.Deploy" "contract deploy"
    command "Contract.Call" "contract call"
    command "Contract.Upgrade" "contract upgrade"
    command "Contract.Query" "contract query"

    group "Transactions" "tx"
    command "Transactions.New" "tx new"
    command "Transactions.Send" "tx send"
    command "Transactions.Get" "tx get"

    group "Hyperblocks" "hyperblock"
    command "Hyperblock.Get" "hyperblock get"

    group "Validator" "validator"
    command "Validator.Stake" "validator stake"
    command "Validator.Unstake" "validator unstake"
    command "Validator.Unjail" "validator unjail"
    command "Validator.Unbond" "validator unbond"
    command "Validator.ChangeRewardAddress" "validator change-reward-address"
    command "Validator.Claim" "validator claim"

    group "Account" "account"
    command "Account.Get" "account get"
    command "Account.GetTransactions" "account get-transactions"
    
    group "Wallet" "wallet"
    command "Wallet.Derive" "wallet derive"
    command "Wallet.Bech32" "wallet bech32"

    group "Testnet" "testnet"
    command "Testnet.Prerequisites" "testnet prerequisites"
    command "Testnet.Config" "testnet config"
    command "Testnet.Start" "testnet start"
    command "Testnet.Clean" "testnet clean"

    group "Network" "network"
    command "Network.NumShards" "network num-shards"
    command "Network.BlockNonce" "network block-nonce"
    command "Network.Chain" "network chain"

    group "Cost" "cost"
    command "Cost.GasPrice" "cost gas-price"
    command "Cost.TxTransfer" "cost tx-transfer"
    command "Cost.ScDeploy" "cost sc-deploy"
    command "Cost.ScCall" "cost sc-call"

    group "Dispatcher" "dispatcher"
    command "Dispatcher.Enqueue" "dispatcher enqueue"
    command "Dispatcher.Dispatch" "dispatcher dispatch"
    command "Dispatcher.DispatchContinuously" "dispatcher dispatch-continuously"
    command "Dispatcher.Clean" "dispatcher clean"

    group "BlockAtlas" "blockatlas"
    command "BlockAtlas.CurrentBlockNumber" "blockatlas current-block-number"
    command "BlockAtlas.BlockByNumber" "blockatlas block-by-number"
    command "BlockAtlas.Transactions" "blockatlas transactions"

    group "Dependencies" "deps"
    command "Dependencies.Install" "deps install"
    command "Dependencies.Check" "deps check"

    group "Configuration" "config"
    command "Configuration.Dump" "config dump"
    command "Configuration.Get" "config get"
    command "Configuration.Set" "config set"

    group "Data" "data"
    command "Data.Dump" "data parse"
    command "Data.Store" "data store"
    command "Data.Load" "data load"
}
