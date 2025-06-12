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

    group "Multisig" "multisig"
    command "Multisig.Deploy" "multisig deploy"
    command "Multisig.Deposit" "multisig deposit"
    command "Multisig.DiscardAction" "multisig discard-action"
    command "Multisig.DiscardBatch" "multisig discard-batch"
    command "Multisig.AddBoardMember" "multisig add-board-member"
    command "Multisig.AddProposer" "multisig add-proposer"
    command "Multisig.RemoveUser" "multisig remove-user"
    command "Multisig.ChangeQuorum" "multisig change-quorum"
    command "Multisig.TransferAndExecute" "multisig transfer-and-execute"
    command "Multisig.TransferAndExecuteEsdt" "multisig transfer-and-execute-esdt"
    command "Multisig.AsyncCall" "multisig async-call"
    command "Multisig.DeployFromSource" "multisig deploy-from-source"
    command "Multisig.UpgradeFromSource" "multisig upgrade-from-source"
    command "Multisig.SignAction" "multisig sign-action"
    command "Multisig.SignBatch" "multisig sign-batch"
    command "Multisig.SignAndPerform" "multisig sign-and-perform"
    command "Multisig.SignBatchAndPerform" "multisig sign-batch-and-perform"
    command "Multisig.UnsignAction" "multisig unsign-action"
    command "Multisig.UnsignBatch" "multisig unsign-batch"
    command "Multisig.UnsignForOutdatedMembers" "multisig unsign-for-outdated-members"
    command "Multisig.PerformAction" "multisig perform-action"
    command "Multisig.PerformBatch" "multisig perform-batch"
    command "Multisig.GetQuorum" "multisig get-quorum"
    command "Multisig.GetNumBoardMembers" "multisig get-num-board-members"
    command "Multisig.GetNumGroups" "multisig get-num-groups"
    command "Multisig.GetNumProposers" "multisig get-num-proposers"
    command "Multisig.GetActionGroup" "multisig get-action-group"
    command "Multisig.GetLastActionGroupId" "multisig get-last-action-group-id"
    command "Multisig.GetLastActionLastIndex" "multisig get-action-last-index"
    command "Multisig.IsSignedBy" "multisig is-signed-by"
    command "Multisig.IsQuorumReached" "multisig is-quorum-reached"
    command "Multisig.GetPendingActions" "multisig get-pending-actions"
    command "Multisig.GetUserRole" "multisig get-user-role"
    command "Multisig.GetBoardMemebers" "multisig get-board-members"
    command "Multisig.GetProposers" "multisig get-proposers"
    command "Multisig.GetActionData" "multisig get-action-data"
    command "Multisig.GetActionSigners" "multisig get-action-signers"
    command "Multisig.GetActionSignersCount" "multisig get-action-signers-count"
    command "Multisig.GetActionValidSignersCount" "multisig get-action-valid-signers-count"
    command "Multisig.ParseProposeAction" "multisig parse-propose-action"

    group "Governance" "governance"
    command "Governance.Propose" "governance propose"
    command "Governance.Vote" "governance vote"
    command "Governance.CloseProposal" "governance close-proposal"
    command "Governance.ClearEndedProposals" "governance clear-ended-proposals"
    command "Governance.ClaimAccumulatedFees" "governance claim-accumulated-fees"
    command "Governance.ChangeConfig" "governance change-config"
    command "Governance.GetVotingPower" "governance get-voting-power"
    command "Governance.GetConfig" "governance get-config"
    command "Governance.GetDelegatedVoteInfo" "governance get-delegated-vote-info"

    group "Environment" "env"
    command "Environment.New" "env new"
    command "Environment.Set" "env set"
    command "Environment.Get" "env get"
    command "Environment.Dump" "env dump"
    command "Environment.Switch" "env switch"
    command "Environment.List" "env list"
    command "Environment.Remove" "env remove"
    command "Environment.Reset" "env reset"

    group "Address" "address"
    command "Address.New" "address new"
    command "Address.List" "address list"
    command "Address.Dump" "address dump"
    command "Address.Get" "address get"
    command "Address.Set" "address set"
    command "Address.Set" "address delete"
    command "Address.Switch" "address switch"
    command "Address.Remove" "address remove"
    command "Address.Reset" "address reset"

    group "Get" "get"
    command "Get.Account" "get account"
    command "Get.Keys" "get keys"
    command "Get.StorageEntry" "get storage-entry"
    command "Get.Token" "get token"
    command "Get.Transaction" "get transaction"
}

generate
