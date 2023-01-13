from typing import Any, List

from multiversx_sdk_cli import cli_shared, validators, utils
from multiversx_sdk_cli.transactions import do_prepare_transaction


def setup_parser(args: List[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "validator", "Stake, UnStake, UnBond, Unjail and other "
                                                                     "actions useful for "
                                                                     "Validators")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "validator", "stake", "Stake value into the Network")
    _add_common_arguments(args, sub)
    sub.add_argument("--reward-address", default="", help="the reward address")
    sub.add_argument("--validators-file", required=not (utils.is_arg_present(args, "--top-up")),
                     help="a JSON file describing the Nodes")
    sub.add_argument("--top-up", action="store_true", default=False,
                     required=not (utils.is_arg_present(args, "--validators-file")), help="Stake value for top up")
    sub.set_defaults(func=do_stake)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unstake", "Unstake value")
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unstake)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unjail", "Unjail a Validator Node")
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unjail)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unbond", "Unbond tokens for a bls key")
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unbond)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "change-reward-address",
                                           "Change the reward address")
    _add_common_arguments(args, sub)
    sub.add_argument("--reward-address", required=True, help="the new reward address")
    sub.set_defaults(func=change_reward_address)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "claim", "Claim rewards")
    _add_common_arguments(args, sub)
    sub.set_defaults(func=do_claim)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unstake-nodes", "Unstake-nodes will unstake "
                                                                                     "nodes for provided bls keys")
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unstake_nodes)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unstake-tokens", "This command will un-stake the "
                                                                                      "given amount (if value is "
                                                                                      "greater than the existing "
                                                                                      "topUp value, it will unStake "
                                                                                      "one or several nodes)")
    _add_common_arguments(args, sub)
    sub.add_argument("--unstake-value", default=0, help="the unstake value")
    sub.set_defaults(func=do_unstake_tokens)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unbond-nodes", "It will unBond nodes")
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_unbond_nodes)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "unbond-tokens", "It will unBond tokens, if "
                                                                                     "provided value is bigger that "
                                                                                     "topUp value will unBond nodes")
    _add_common_arguments(args, sub)
    sub.add_argument("--unbond-value", default=0, help="the unbond value")
    sub.set_defaults(func=do_unbond_tokens)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "clean-registered-data", "Deletes duplicated keys "
                                                                                             "from registered data")
    _add_common_arguments(args, sub)
    sub.set_defaults(func=do_clean_registered_data)

    sub = cli_shared.add_command_subparser(subparsers, "validator", "restake-unstaked-nodes", "It will reStake UnStaked nodes")
    _add_common_arguments(args, sub)
    _add_nodes_arg(sub)
    sub.set_defaults(func=do_restake_unstaked_nodes)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_common_arguments(args: List[str], sub: Any):
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False, with_estimate_gas=True)
    cli_shared.add_broadcast_args(sub, relay=False)
    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")


def _add_nodes_arg(sub: Any):
    sub.add_argument("--nodes-public-keys", required=True, help="the public keys of the nodes as CSV (addrA,addrB)")


def do_stake(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_stake(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def do_unstake(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_unstake(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def do_unjail(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_unjail(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def do_unbond(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_unbond(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def change_reward_address(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_change_reward_address(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def do_claim(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_claim(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def do_unstake_nodes(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_unstake_nodes(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def do_unstake_tokens(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_unstake_tokens(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def do_unbond_nodes(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_unbond_nodes(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def do_unbond_tokens(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_unbond_tokens(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def do_clean_registered_data(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_clean_registered_data(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)


def do_restake_unstaked_nodes(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_restake_unstaked_nodes(args)
    tx = do_prepare_transaction(args)

    cli_shared.send_or_simulate(tx, args)
