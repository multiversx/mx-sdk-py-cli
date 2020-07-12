from erdpy import cli_shared
import logging
from typing import Any

from erdpy import facade

logger = logging.getLogger("cli.network")


def setup_parser(subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "network", "Get Network parameters, such as number of shards, chain identifier etc.")
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "network", "num-shards", "Get the number of shards.")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_num_shards)

    sub = cli_shared.add_command_subparser(subparsers, "network", "block-nonce", "Get the latest block nonce, by shard.")
    cli_shared.add_proxy_arg(sub)
    sub.add_argument("--shard", required=True, help="the shard ID (use 4294967295 for metachain)")
    sub.set_defaults(func=get_last_block_nonce)

    sub = cli_shared.add_command_subparser(subparsers, "network", "chain", "Get the chain identifier.")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_chain_id)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def get_num_shards(args: Any):
    facade.get_num_shards(args)


def get_last_block_nonce(args: Any):
    facade.get_last_block_nonce(args)


def get_chain_id(args: Any):
    facade.get_chain_id(args)
