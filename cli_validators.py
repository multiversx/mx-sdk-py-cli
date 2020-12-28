from typing import Any

from erdpy import cli_shared, validators
from erdpy.transactions import do_prepare_transaction


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "validator", "Stake, Unjail and other actions useful for "
                                                                     "Validators")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "validator", "stake", "Stake value into the Network")
    _add_common_arguments(sub)
    sub.add_argument("--reward-address", default="", help="the reward address")
    sub.add_argument("--validators-file", required=True, help="a JSON file describing the Nodes")
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

    sub = cli_shared.add_command_subparser(subparsers, "validator", "change-reward-address",
                                           "Change the reward address")
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
    cli_shared.add_broadcast_args(sub, relay=False)
    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")


def _add_nodes_arg(sub: Any):
    sub.add_argument("--nodes-public-keys", required=True, help="the public keys of the nodes as CSV (addrA,addrB)")


def do_stake(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_stake(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def do_unstake(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_unstake(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def do_unjail(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_unjail(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def do_unbond(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_unbond(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def change_reward_address(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_change_reward_address(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)


def do_claim(args: Any):
    cli_shared.check_broadcast_args(args)
    cli_shared.prepare_nonce_in_args(args)
    validators.prepare_args_for_claim(args)
    tx = do_prepare_transaction(args)

    try:
        cli_shared.send_or_simulate(tx, args)
    finally:
        tx.dump_to(args.outfile)
