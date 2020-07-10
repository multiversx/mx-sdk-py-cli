import sys

from erdpy import config, facade
from erdpy.utils import is_arg_present


def setup_parser(subparsers):
    parser = subparsers.add_parser("validator")
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("stake")
    _add_common_arguments(sub)
    sub.add_argument("--number-of-nodes", required=True)
    sub.add_argument("--nodes-public-keys", required=True)
    sub.add_argument("--reward-address", default="")
    sub.set_defaults(func=do_stake)

    sub = subparsers.add_parser("unstake")
    _add_common_arguments(sub)
    sub.add_argument("--nodes-public-keys", required=True)
    sub.set_defaults(func=do_unstake)

    sub = subparsers.add_parser("unjail")
    _add_common_arguments(sub)
    sub.add_argument("--nodes-public-keys", required=True)
    sub.set_defaults(func=do_unjail)

    sub = subparsers.add_parser("unbond")
    _add_common_arguments(sub)
    sub.add_argument("--nodes-public-keys", required=True)
    sub.set_defaults(func=do_unbond)

    sub = subparsers.add_parser("change-reward-address")
    _add_common_arguments(sub)
    sub.add_argument("--reward-address", required=True)
    sub.set_defaults(func=change_reward_address)

    sub = subparsers.add_parser("claim")
    _add_common_arguments(sub)
    sub.set_defaults(func=do_claim)


def _add_common_arguments(sub):
    sub.add_argument("--pem", required=not(is_arg_present("--keyfile", sys.argv)))
    sub.add_argument("--keyfile", required=not(is_arg_present("--pem", sys.argv)))
    sub.add_argument("--passfile", required=not(is_arg_present("--pem", sys.argv)))

    sub.add_argument("--nonce", type=int, required=not("--recall-nonce" in sys.argv))
    sub.add_argument("--recall-nonce", action="store_true", default=False)
    sub.add_argument("--value", default="0")
    sub.add_argument("--gas-price", default=config.DEFAULT_GAS_PRICE)
    sub.add_argument("--gas-limit", required=not("--estimate-gas" in sys.argv))
    sub.add_argument("--estimate-gas", action="store_true", default=False)
    sub.add_argument("--chain", default=config.get_chain_id())
    sub.add_argument("--version", type=int, default=config.get_tx_version())
    sub.add_argument("--proxy", required=True)


def do_stake(args):
    facade.prepare_and_send_stake_transaction(args)


def do_unstake(args):
    facade.prepare_and_send_unstake_transaction(args)


def do_unbond(args):
    facade.prepare_and_send_unbond_transaction(args)


def do_unjail(args):
    facade.prepare_and_send_unjail_transaction(args)


def change_reward_address(args):
    facade.prepare_and_send_change_reward_address_transaction(args)


def do_claim(args):
    facade.prepare_and_send_claim_transaction(args)
