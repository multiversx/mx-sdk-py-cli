#!/usr/bin/env bash

export PYTHONPATH=.

CLI="python3 -m multiversx_sdk_cli.cli"
CLI_ALIAS="mxpy"

code() {
    printf "\n\`\`\`\n" >> CLI.md
}

group() {
    printf "## Group **$1**\n\n" >> CLI.md

    code
    printf "$ ${CLI_ALIAS} $2 --help\n" >> CLI.md
    ${CLI} ${2} --help >> CLI.md
    code
}

command() {
    printf "### $1\n\n" >> CLI.md

    code
    printf "$ ${CLI_ALIAS} $2 --help\n" >> CLI.md
    ${CLI} ${2} --help >> CLI.md
    code
}

generate() {
    echo -n > CLI.md
    printf "# Command Line Interface\n\n" >> CLI.md

    printf "## Overview\n\n" >> CLI.md
    printf "**${CLI_ALIAS}** exposes a number of CLI **commands**, organized within **groups**.\n\n" >> CLI.md

    code
    printf "$ ${CLI_ALIAS} --help\n" >> CLI.md
    ${CLI} --help >> CLI.md
    code

    group "Contract" "contract"
    command "Contract.Deploy" "contract deploy"
    command "Contract.Call" "contract call"
    command "Contract.Upgrade" "contract upgrade"
    command "Contract.Query" "contract query"
    command "Contract.Verify" "contract verify"
    command "Contract.ReproducibleBuild" "contract reproducible-build"

    group "Transactions" "tx"
    command "Transactions.New" "tx new"
    command "Transactions.Send" "tx send"
    command "Transactions.Sign" "tx sign"
    command "Transactions.Relay" "tx relay"

    group "Validator" "validator"
    command "Validator.Stake" "validator stake"
    command "Validator.Unstake" "validator unstake"
    command "Validator.Unjail" "validator unjail"
    command "Validator.Unbond" "validator unbond"
    command "Validator.ChangeRewardAddress" "validator change-reward-address"
    command "Validator.Claim" "validator claim"
    command "Validator.UnstakeNodes" "validator unstake-nodes"
    command "Validator.UnstakeTokens" "validator unstake-tokens"
    command "Validator.UnbondNodes" "validator unbond-nodes"
    command "Validator.UnbondTokens" "validator unbond-tokens"
    command "Validator.CleanRegisteredData" "validator clean-registered-data"
    command "Validator.RestakeUnstakedNodes" "validator restake-unstaked-nodes"

    group "StakingProvider" "staking-provider"
    command "StakingProvider.CreateNewDelegationContract" "staking-provider create-new-delegation-contract"
    command "StakingProvider.GetContractAddress" "staking-provider get-contract-address"
    command "StakingProvider.AddNodes" "staking-provider add-nodes"
    command "StakingProvider.RemoveNodes" "staking-provider remove-nodes"
    command "StakingProvider.StakeNodes" "staking-provider stake-nodes"
    command "StakingProvider.UnbondNodes" "staking-provider unbond-nodes"
    command "StakingProvider.UnstakeNodes" "staking-provider unstake-nodes"
    command "StakingProvider.UnjailNodes" "staking-provider unjail-nodes"
    command "StakingProvider.Delegate" "staking-provider delegate"
    command "StakingProvider.ClaimRewards" "staking-provider claim-rewards"
    command "StakingProvider.RedelegateRewards" "staking-provider redelegate-rewards"
    command "StakingProvider.Undelegate" "staking-provider undelegate"
    command "StakingProvider.Withdraw" "staking-provider withdraw"
    command "StakingProvider.ChangeServiceFee" "staking-provider change-service-fee"
    command "StakingProvider.ModifyDelegationCap" "staking-provider modify-delegation-cap"
    command "StakingProvider.AutomaticActivation" "staking-provider automatic-activation"
    command "StakingProvider.RedelegateCap" "staking-provider redelegate-cap"
    command "StakingProvider.SetMetadata" "staking-provider set-metadata"
    command "StakingProvider.MakeDelegationContractFromValidator" "staking-provider make-delegation-contract-from-validator"

    group "Wallet" "wallet"
    command "Wallet.New" "wallet new"
    command "Wallet.Convert" "wallet convert"
    command "Wallet.Bech32" "wallet bech32"
    command "Wallet.SignMessage" "wallet sign-message"
    command "Wallet.VerifyMessage" "wallet verify-message"

    group "ValidatorWallet" "validator-wallet"
    command "Wallet.New" "validator-wallet new"
    command "Wallet.Convert" "validator-wallet convert"
    command "Wallet.SignMessage" "validator-wallet sign-message"
    command "Wallet.VerifyMessage" "validator-wallet verify-message-signature"

    group "Localnet" "localnet"
    command "Localnet.Setup" "localnet setup"
    command "Localnet.New" "localnet new"
    command "Localnet.Prerequisites" "localnet prerequisites"
    command "Localnet.Build" "localnet build"
    command "Localnet.Config" "localnet config"
    command "Localnet.Start" "localnet start"
    command "Localnet.Clean" "localnet clean"

    group "Dependencies" "deps"
    command "Dependencies.Install" "deps install"
    command "Dependencies.Check" "deps check"

    group "Configuration" "config"
    command "Configuration.Dump" "config dump"
    command "Configuration.Get" "config get"
    command "Configuration.Set" "config set"
    command "Configuration.New" "config new"
    command "Configuration.Switch" "config switch"
    command "Configuration.List" "config list"
    command "Configuration.Reset" "config reset"

    group "Data" "data"
    command "Data.Dump" "data parse"
    command "Data.Store" "data store"
    command "Data.Load" "data load"

    group "Faucet" "faucet"
    command "Faucet.Request" "faucet request"

    group "Environment" "env"
    command "Environment.New" "env new"
    command "Environment.Set" "env set"
    command "Environment.Get" "env get"
    command "Environment.Dump" "env dump"
    command "Environment.Switch" "env switch"
    command "Environment.List" "env list"
    command "Environment.Remove" "env remove"
    command "Environment.Reset" "env reset"
}

generate
