from typing import Any

from erdpy import cli_shared, facade


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "validator", "Stake, Unjail and other actions useful for "
                                                                     "Validators")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "validator", "stake", "Stake value into the Network")
    _add_common_arguments(sub)
    sub.add_argument("--reward-address", default="", help="the reward address")
    sub.add_argument("--validators-data-file", required=True)
    sub.set_defaults(func=do_stake)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unstake", "Unstake value")
    _add_common_arguments(sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unstake)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unjail", "Unjail a Validator Node")
    _add_common_arguments(sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unjail)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unbond", "Unbond")
    _add_common_arguments(sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unbond)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "change-reward-address", "Change the reward address")
    _add_common_arguments(sub)
    sub.add_argument("--reward-address", required=True, help="the new reward address")
    sub.set_defaults(func=change_reward_address)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "claim", "Claim rewards")
    _add_common_arguments(sub)
    sub.set_defaults(func=do_claim)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_common_arguments(sub: Any):
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_wallet_args(sub)
    cli_shared.add_tx_args(sub, with_receiver=False, with_data=False, with_estimate_gas=True)


def _add_nodes_arg(sub: Any):
    sub.add_argument("--nodes-public-keys", required=True, help="the public keys of the nodes as CSV (addrA,addrB)")


def do_stake(args: Any):
    facade.prepare_and_send_stake_transaction(args)


def do_unstake(args: Any):
    facade.prepare_and_send_unstake_transaction(args)


def do_unbond(args: Any):
    facade.prepare_and_send_unbond_transaction(args)


def do_unjail(args: Any):
    facade.prepare_and_send_unjail_transaction(args)


def change_reward_address(args: Any):
    facade.prepare_and_send_change_reward_address_transaction(args)


def do_claim(args: Any):
    facade.prepare_and_send_claim_transaction(args)
